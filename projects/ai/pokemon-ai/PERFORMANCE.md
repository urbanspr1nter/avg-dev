# Performance Optimization Report

## Result

**Before:** ~15 fps, ~0.25x realtime, visible frame skipping, broken audio
**After:** ~62 fps, 1.04x realtime, smooth rendering, real-time audio

Benchmarked on M3 Max running Pokemon Red (MBC3) with 60-frame emulation-only measurement (no frontend overhead).

## Methodology

Each optimization was profiled with `cProfile`, targeting the highest `tottime` function first. Tests (990 total) were run after every change to ensure correctness. Benchmarks were run 3x for consistency.

---

## Optimizations (chronological)

### 1. Framebuffer Rendering — `src/frontend/pygame_frontend.py`

**Problem:** `_render_frame()` called `surface.set_at()` 23,040 times per frame (160x144 pixels). Each call crosses the Python-C boundary with coordinate tuple creation.

**Before:**
```python
def _render_frame(self):
    framebuffer = self._gb.get_framebuffer()
    for y in range(GB_HEIGHT):
        for x in range(GB_WIDTH):
            color = DMG_PALETTE[framebuffer[y][x]]
            self._surface.set_at((x, y), color)  # 23,040 calls per frame
    scaled = pygame.transform.scale(self._surface, ...)
    self._screen.blit(scaled, (0, 0))
    pygame.display.flip()
```

**After:**
```python
def __init__(self, ...):
    # Pre-allocate a flat RGB buffer instead of a Surface
    self._pixel_buffer = bytearray(GB_WIDTH * GB_HEIGHT * 3)

def _render_frame(self):
    framebuffer = self._gb.get_framebuffer()
    buf = self._pixel_buffer
    offset = 0
    for y in range(GB_HEIGHT):
        row = framebuffer[y]
        for x in range(GB_WIDTH):
            r, g, b = DMG_PALETTE[row[x]]
            buf[offset] = r
            buf[offset + 1] = g
            buf[offset + 2] = b
            offset += 3
    # Single C-level call to build the surface from raw bytes
    image = pygame.image.frombuffer(buf, (GB_WIDTH, GB_HEIGHT), 'RGB')
    scaled = pygame.transform.scale(image, (...))
    self._screen.blit(scaled, (0, 0))
    pygame.display.flip()
```

**Why it works:** 23,040 `set_at()` calls (each creating a coordinate tuple and crossing into C) are replaced by a single `frombuffer()` call that reads a contiguous byte buffer.

---

### 2. APU Batch Ticking — `src/apu/apu.py` + channel files

**Problem:** APU.tick() was called per-T-cycle (~4.2M times/sec), with each call invoking 4 channel tick methods individually. This consumed 53% of total CPU time (0.380s/0.717s).

**Before (channel tick — called once per T-cycle):**
```python
# pulse_channel.py
def tick(self, cycles):   # cycles was always 1
    self._freq_timer -= 1
    if self._freq_timer == 0:
        self._freq_timer = (2048 - self._period) * 4
        self._duty_pos = (self._duty_pos + 1) & 7
```

**After (channel tick — called with batched cycle count):**
```python
# pulse_channel.py
def tick(self, cycles):
    if not self._enabled:
        return
    self._freq_timer -= cycles          # Subtract full batch at once
    while self._freq_timer <= 0:        # Handle multiple expirations
        self._freq_timer += (2048 - self._period) * 4
        self._duty_pos = (self._duty_pos + 1) & 7
```

**Before (APU tick — per-cycle loop):**
```python
def tick(self, cycles):
    for _ in range(cycles):       # 4-20 iterations per instruction
        self._tick_single_cycle()  # Frame sequencer + sample + 4 channels
```

**After (APU tick — event boundary batching):**
```python
def tick(self, cycles):
    if not self._power:
        return
    remaining = cycles
    while remaining > 0:
        # Jump directly to the next event (frame sequencer step or sample point)
        cycles_to_fs = 8192 - self._fs_counter
        cycles_to_sample = int(self._sample_period - self._sample_counter) + 1
        step = min(remaining, cycles_to_fs, cycles_to_sample)

        self._fs_counter += step
        self._sample_counter += step
        remaining -= step

        self._ch1.tick(step)   # Each channel handles the full batch
        self._ch2.tick(step)
        self._ch3.tick(step)
        self._ch4.tick(step)

        if self._fs_counter >= 8192:
            self._fs_counter = 0
            self._clock_frame_sequencer()
        if self._sample_counter >= self._sample_period:
            self._sample_counter -= self._sample_period
            self._sample_buffer.append(self._mix_channels())
```

**Why it works:** Instead of iterating 4-20 times per instruction (one per T-cycle), we compute the next event boundary and jump there directly. Most instructions (4-16 cycles) don't cross any boundary, so the `while` loop runs just once.

**Impact:** APU 0.380s → 0.092s (76% reduction)

---

### 3. PPU Batch Ticking — `src/ppu/ppu.py`

**Problem:** PPU.tick() iterated one dot at a time through the mode state machine (456 dots/scanline x 154 scanlines x 60 fps = ~4.2M iterations/sec).

**Before:**
```python
def tick(self, cycles):
    for _ in range(cycles):
        self._dot += 1
        if self._dot == 80:
            self._set_mode(3)
        elif self._dot == 252:
            self._set_mode(0)
            self._render_scanline()
        elif self._dot == 456:
            # ... advance scanline
```

**After:**
```python
def tick(self, cycles):
    if not (self._lcdc & 0x80):
        return

    dot = self._dot
    ly = self._ly

    # Compute next event boundary
    if ly < 144:
        if dot < 80:     next_event = 80
        elif dot < 252:  next_event = 252
        else:            next_event = 456
    else:
        next_event = 456

    # Fast path: no event boundary crossed (most common)
    gap = next_event - dot
    if cycles < gap:
        self._dot = dot + cycles
        return

    # Slow path: event boundary crossed
    remaining = cycles
    while remaining > 0:
        # ... advance to next boundary, process mode transitions
```

**Why it works:** ~95% of calls take the fast path (a single addition + comparison). The `while` loop only runs when an instruction's cycles actually cross a mode transition boundary (dots 80, 252, or 456).

**Impact:** PPU.tick 0.167s → 0.077s (54% reduction)

---

### 4. Timer Batch Ticking — `src/timer/gb_timer.py`

**Problem:** Timer.tick() iterated one T-cycle at a time, checking for falling edges of the selected internal counter bit each cycle.

**Before:**
```python
def tick(self, cycles):
    for _ in range(cycles):
        old_bit = (self._internal_counter >> self._clock_bit) & 1
        self._internal_counter = (self._internal_counter + 1) & 0xFFFF
        new_bit = (self._internal_counter >> self._clock_bit) & 1
        if old_bit == 1 and new_bit == 0:  # Falling edge
            self._tima += 1
            if self._tima > 0xFF:
                self._tima = self._tma
                self._request_timer_interrupt()
```

**After:**
```python
def tick(self, cycles):
    old_counter = self._internal_counter
    unwrapped_new = old_counter + cycles
    self._internal_counter = unwrapped_new & 0xFFFF

    if not (self._tac & 0x04):  # Timer disabled
        return

    clock_bit = self.TAC_CLOCK_BITS[self._tac & 0x03]
    shift = clock_bit + 1
    # Count falling edges in O(1) using integer division
    edges = (unwrapped_new >> shift) - (old_counter >> shift)

    for _ in range(edges):   # Only loops for actual TIMA increments (rare)
        self._tima += 1
        if self._tima > 0xFF:
            self._tima = self._tma
            self._request_timer_interrupt()
```

**Why it works:** Instead of checking each T-cycle for a falling edge, we compute the number of edges crossed algebraically. A right-shift by `(clock_bit + 1)` gives the number of complete periods, so the difference gives the edge count. For a 1024-cycle timer period, this replaces 1024 iterations with 2 shifts and a subtract.

**Impact:** Timer.tick 0.347s → 0.058s (83% reduction)

---

### 5. Opcode Pre-indexing — `src/cpu/gb_cpu.py`

**Problem:** Each instruction did string formatting + nested dict lookup to find opcode metadata.

**Before:**
```python
# Per-instruction lookup (327K times per 30 frames)
key = f"0x{opcode:02X}"                    # String allocation every time
opcode_info = opcodes_db["unprefixed"][key]  # Nested dict lookup
```

**After:**
```python
# At CPU init: pre-index into flat 256-element lists
self._unprefixed_info = [None] * 256
for i in range(256):
    key = f"0x{i:02X}"
    if key in opcodes_db["unprefixed"]:
        self._unprefixed_info[i] = opcodes_db["unprefixed"][key]

# Per-instruction: direct list index (no string, no hash)
opcode_info = self._unprefixed_info[opcode]  # O(1) array index
```

**Why it works:** List indexing (`list[i]`) is a direct pointer offset in C. Dict lookup requires hashing the key string, comparing, and following hash chains. Eliminates a string allocation per instruction.

---

### 6. CPU Run Loop Rewrite — `src/cpu/gb_cpu.py`

**Problem:** The run loop had excessive per-instruction overhead from attribute lookups, operand processing, and dispatch logic.

**Before:**
```python
def run(self, max_cycles=-1):
    while True:
        if max_cycles >= 0 and self.current_cycles >= max_cycles:
            break
        # ... lots of self.xxx attribute accesses per iteration
        handler = self.opcode_handlers.get(opcode)  # Dict lookup
        meta = self._unprefixed_meta[opcode]         # Separate lookup
        # ...
        if self._timer: self._timer.tick(cycles_used)  # Attr lookup each time
        if self._ppu:   self._ppu.tick(cycles_used)
        if self._apu:   self._apu.tick(cycles_used)
```

**After:**
```python
def run(self, max_cycles=-1):
    # Cache everything as locals (2x faster than self.xxx)
    registers = self.registers
    interrupts = self.interrupts
    memory_get = self.memory.get_value
    mem_array = self.memory.memory
    current_cycles = self.current_cycles

    # Cache bound methods (skip attr lookup on every tick)
    timer_tick = timer.tick if timer else None
    ppu_tick = ppu.tick if ppu else None
    apu_tick = apu.tick if apu else None

    # Combined meta+handler in one list (one lookup instead of two)
    dispatch = self._dispatch      # dispatch[opcode] = (info, fetch_size, ops, idx, handler)
    cb_dispatch = self._cb_dispatch

    while current_cycles < max_cycles:   # Simplified loop condition
        # ... use cached locals throughout
        entry = dispatch[opcode]          # Single lookup for meta + handler
        opcode_info, fetch_size, pre_ops, fetch_idx, handler = entry

        cycles_used = handler(self, opcode_info)
        current_cycles += cycles_used
        if timer_tick: timer_tick(cycles_used)   # Bound method, no attr lookup
        if ppu_tick:   ppu_tick(cycles_used)
        if apu_tick:   apu_tick(cycles_used)

    self.current_cycles = current_cycles   # Write back once at exit
```

**Key sub-optimizations:**
- `_build_opcode_meta()` pre-builds operand dicts once at init; only the `value` field is mutated at runtime (no per-instruction dict/list creation)
- `_dispatch` combines metadata + handler into a single 256-element list, replacing two separate lookups
- `while current_cycles < max_cycles` replaces `while True` + `if max_cycles >= 0 and ...`
- `current_cycles` is a local variable, written back to `self.current_cycles` only at loop exit
- Interrupt check uses direct `mem_array[0xFF0F] & mem_array[0xFFFF]` instead of `memory.get_value()`

**Impact:** run() self-time 0.801s → 0.423s (47% reduction)

---

### 7. Memory Bus Optimization — `src/memory/gb_memory.py`

**Problem:** ROM reads (the most frequent operation — every instruction fetch) went through three method calls: `memory.get_value()` → `cartridge.read()` → `mbc.read()`.

**Before:**
```python
def __init__(self):
    self.memory = [0] * 0x10000          # Python list (slow indexing)

def get_value(self, address):
    if address <= 0x7FFF:
        if self._cartridge is not None:
            return self._cartridge.read(address)  # -> mbc.read(address)
```

**After:**
```python
def __init__(self):
    self.memory = bytearray(0x10000)     # C-level byte array (fast indexing)
    self._mbc = None
    self._rom_data = None

def load_cartridge(self, cartridge):
    self._cartridge = cartridge
    self._mbc = cartridge._mbc           # Cache MBC reference
    self._rom_data = cartridge._mbc._rom_data  # Cache ROM bytes reference

def get_value(self, address):
    if address <= 0x7FFF:
        rom_data = self._rom_data
        if rom_data is not None:
            if address <= 0x3FFF:
                return rom_data[address]                  # Direct bytes index
            offset = (self._mbc._rom_bank * 0x4000) + (address - 0x4000)
            return rom_data[offset] if offset < len(rom_data) else 0xFF
        return self.memory[address]
```

**Interrupt register fast path (in CPU):**
```python
# Before: goes through full get_value() dispatch
if_val = self.memory.get_value(0xFF0F)
ie_val = self.memory.get_value(0xFFFF)

# After: direct array access, bypassing all dispatch
mem = self.memory.memory
if mem[0xFF0F] & mem[0xFFFF]:
    ...
```

**Why it works:**
- Inlining ROM reads eliminates 2 method calls (cartridge.read + mbc.read) for the most frequent operation (393K calls per 30 frames)
- `bytearray` indexing uses C-level byte access with no Python int object creation, vs `list` indexing which creates a new Python int for every read
- Direct `memory.memory[0xFF0F]` for interrupt checks avoids the entire if/elif dispatch chain

**Impact:** Eliminated 786K method calls per 30 frames. get_value 0.421s → 0.108s (74% reduction).

---

### 8. Flag and Register Access — `src/cpu/gb_cpu.py`

**Problem:** `set_flag()` used a 4-way if/elif chain comparing flag name strings on every call (207K calls/30 frames).

**Before:**
```python
def set_flag(self, flag, value):
    flags = self.registers.AF & 0xFF
    if flag == "Z":            # String comparison 1
        if value:
            flags |= 0x80
        else:
            flags &= ~0x80
    elif flag == "N":          # String comparison 2
        if value:
            flags |= 0x40
        else:
            flags &= ~0x40
    elif flag == "H":          # String comparison 3
        ...
    elif flag == "C":          # String comparison 4
        ...
    self.registers.AF = (self.registers.AF & 0xFF00) | flags
```

**After:**
```python
_FLAG_BITS = {"Z": 0x80, "N": 0x40, "H": 0x20, "C": 0x10}

def get_flag(self, flag):
    return (self.registers.AF & self._FLAG_BITS[flag]) != 0

def set_flag(self, flag, value):
    bit = self._FLAG_BITS[flag]   # Single dict lookup
    if value:
        self.registers.AF |= bit
    else:
        self.registers.AF = (self.registers.AF & ~bit) & 0xFFFF
```

**Why it works:** Dict lookup is O(1) with a single hash comparison, vs scanning through up to 4 string comparisons. Also eliminates the intermediate `flags` variable and extra `& 0xFF` / `& 0xFF00` masking.

**Impact:** set_flag 0.058s → 0.043s (26% reduction)

---

### 9. APU Channel Tick Inlining — `src/apu/apu.py`

**Problem:** The APU fast path (no event boundary crossed) still called 4 channel `.tick()` methods per invocation (327K x 4 = 1.3M method calls per 30 frames). Each call has ~100-200ns Python overhead for what's usually just `freq_timer -= cycles`.

**Before (fast path):**
```python
def tick(self, cycles):
    if not self._power:
        return
    fs_counter = self._fs_counter + cycles
    sample_counter = self._sample_counter + cycles
    if fs_counter < 8192 and sample_counter < self._sample_period:
        self._fs_counter = fs_counter
        self._sample_counter = sample_counter
        self._ch1.tick(cycles)   # Method call overhead
        self._ch2.tick(cycles)   # Method call overhead
        self._ch3.tick(cycles)   # Method call overhead
        self._ch4.tick(cycles)   # Method call overhead
        return
```

**After (inlined channel logic):**
```python
def tick(self, cycles):
    if not self._power:
        return
    fs_counter = self._fs_counter + cycles
    sample_counter = self._sample_counter + cycles
    if fs_counter < 8192 and sample_counter < self._sample_period:
        self._fs_counter = fs_counter
        self._sample_counter = sample_counter
        # Inline pulse channel 1 (no method call)
        ch1 = self._ch1
        if ch1._enabled:
            ch1._freq_timer -= cycles
            if ch1._freq_timer <= 0:
                while ch1._freq_timer <= 0:
                    ch1._freq_timer += (2048 - ch1._period) * 4
                    ch1._duty_pos = (ch1._duty_pos + 1) & 7
        # Inline pulse channel 2
        ch2 = self._ch2
        if ch2._enabled:
            ch2._freq_timer -= cycles
            if ch2._freq_timer <= 0:
                while ch2._freq_timer <= 0:
                    ch2._freq_timer += (2048 - ch2._period) * 4
                    ch2._duty_pos = (ch2._duty_pos + 1) & 7
        # Inline wave channel (includes wave RAM sample read)
        ch3 = self._ch3
        if ch3._enabled:
            ch3._freq_timer -= cycles
            if ch3._freq_timer <= 0:
                while ch3._freq_timer <= 0:
                    ch3._freq_timer += (2048 - ch3._period) * 2
                    ch3._wave_pos = (ch3._wave_pos + 1) & 31
                    byte_idx = ch3._wave_pos >> 1
                    if ch3._wave_pos & 1:
                        ch3._sample_buffer = ch3._wave_ram[byte_idx] & 0x0F
                    else:
                        ch3._sample_buffer = (ch3._wave_ram[byte_idx] >> 4) & 0x0F
        # Inline noise channel (includes LFSR + divisor table)
        ch4 = self._ch4
        if ch4._enabled:
            ch4._freq_timer -= cycles
            if ch4._freq_timer <= 0:
                while ch4._freq_timer <= 0:
                    divisor = _NOISE_DIVISOR_TABLE[ch4._divisor_code]
                    period = divisor << ch4._clock_shift
                    ch4._freq_timer += period if period else 1
                    xor_bit = (ch4._lfsr & 1) ^ ((ch4._lfsr >> 1) & 1)
                    ch4._lfsr = (ch4._lfsr >> 1) | (xor_bit << 14)
                    if ch4._width_mode:
                        ch4._lfsr = (ch4._lfsr & ~0x40) | (xor_bit << 6)
        return
```

Note: `_NOISE_DIVISOR_TABLE` is cached at module level to avoid class attribute lookup:
```python
_NOISE_DIVISOR_TABLE = NoiseChannel.DIVISOR_TABLE
```

**Why it works:** Eliminates 1.3M method calls per 30 frames. For disabled channels (common during title screens), the check `if ch._enabled` is a single attribute read vs a full method call + attribute read inside the method. For enabled channels where the timer doesn't expire (most common case), it's just `ch._freq_timer -= cycles` + one comparison.

**Impact:** APU.tick cumtime 0.540s → 0.257s (52% reduction)

---

### 10. APU Mixer Optimization — `src/apu/apu.py`

**Problem:** `_mix_channels()` allocated temporary lists and used loops for what's a fixed 4-channel mix.

**Before:**
```python
def _mix_channels(self):
    channels = [self._ch1, self._ch2, self._ch3, self._ch4]  # List creation
    dac_outputs = []
    for ch in channels:                          # Loop + append
        if ch._dac_enabled:
            dac_outputs.append((ch.get_output() / 7.5) - 1.0)
        else:
            dac_outputs.append(0.0)

    left = 0.0
    right = 0.0
    for i, dac_out in enumerate(dac_outputs):    # enumerate overhead
        if self._nr51 & (0x10 << i): left += dac_out
        if self._nr51 & (0x01 << i): right += dac_out

    left /= 4.0                                  # Two-step normalize + volume
    right /= 4.0
    left_volume = ((self._nr50 >> 4) & 0x07) + 1
    left *= left_volume / 8.0
    # ...
    left, self._hpf_capacitor_left = self._high_pass(left, ...)   # Method call
    right, self._hpf_capacitor_right = self._high_pass(right, ...) # Method call
    return (left, right)
```

**After:**
```python
def _mix_channels(self):
    # Direct DAC reads (no list, no loop)
    ch1 = self._ch1
    d1 = (ch1.get_output() / 7.5) - 1.0 if ch1._dac_enabled else 0.0
    ch2 = self._ch2
    d2 = (ch2.get_output() / 7.5) - 1.0 if ch2._dac_enabled else 0.0
    ch3 = self._ch3
    d3 = (ch3.get_output() / 7.5) - 1.0 if ch3._dac_enabled else 0.0
    ch4 = self._ch4
    d4 = (ch4.get_output() / 7.5) - 1.0 if ch4._dac_enabled else 0.0

    nr51 = self._nr51
    left = 0.0
    right = 0.0
    # Unrolled panning (no enumerate, no shift computation)
    if nr51 & 0x10: left += d1
    if nr51 & 0x01: right += d1
    if nr51 & 0x20: left += d2
    if nr51 & 0x02: right += d2
    if nr51 & 0x40: left += d3
    if nr51 & 0x04: right += d3
    if nr51 & 0x80: left += d4
    if nr51 & 0x08: right += d4

    # Combined normalize + volume in one multiply (/4.0 * vol/8.0 = * vol/32.0)
    nr50 = self._nr50
    left *= (((nr50 >> 4) & 0x07) + 1) / 32.0
    right *= ((nr50 & 0x07) + 1) / 32.0

    # Inlined high-pass filter (no method calls)
    charge = self._hpf_charge_factor
    cap_l = self._hpf_capacitor_left
    out_l = left - cap_l
    self._hpf_capacitor_left = left - out_l * charge
    cap_r = self._hpf_capacitor_right
    out_r = right - cap_r
    self._hpf_capacitor_right = right - out_r * charge

    return (out_l, out_r)
```

**Why it works:** Eliminates 2 list allocations, an `enumerate()` iterator, 2 `_high_pass()` method calls, and several redundant multiplications per sample (24K samples per 30 frames).

**Impact:** _mix_channels 0.070s → 0.038s (46% reduction)

---

## Profile Comparison (30 frames, cProfile)

| Function | Before | After | Reduction |
|---|---|---|---|
| Total wall time | 2.85s | 1.41s | 51% |
| run() self | 0.80s | 0.42s | 47% |
| APU.tick | 0.54s | 0.26s | 52% |
| PPU.tick | 0.39s | 0.08s | 80% |
| Timer.tick | 0.35s | 0.06s | 83% |
| memory.get_value | 0.42s | 0.11s | 74% |
| cartridge.read+mbc.read | 0.18s | 0.00s | 100% |
| _render_scanline | 0.24s | 0.13s | 46% |
| set_flag | 0.06s | 0.04s | 26% |

Note: cProfile adds ~2x overhead. Without profiling, the emulator runs at 62 fps / 1.04x realtime.

---

## Principles Applied

1. **Profile first** — `cProfile` identified the actual bottleneck before each change. Gut instinct was often wrong (initial assumption was rendering; actual bottleneck was APU at 53% of runtime).

2. **Batch to event boundaries** — The single biggest pattern. All subsystems (APU, PPU, Timer) originally iterated per-T-cycle. Advancing in chunks between event boundaries eliminated millions of Python loop iterations. The key insight: compute *when* the next interesting thing happens and skip directly there, rather than checking every cycle.

3. **Eliminate method call overhead** — Python method calls cost ~100-200ns each. Inlining hot-path logic (channel ticks, ROM reads, high-pass filter) eliminated millions of calls. The tradeoff is readability vs performance; inlining was only done for the fast path while keeping the slow path clean.

4. **Cache as locals** — Python local variable access is ~2x faster than attribute lookup (`self.x`). Caching frequently-accessed attributes at the top of hot loops made a measurable difference. This includes caching class constants as instance variables and caching bound methods to skip the attribute-lookup-then-call pattern.

5. **Use C-backed data structures** — `bytearray` instead of `list` for memory, `bytes` for ROM data, `pygame.image.frombuffer()` instead of `set_at()`. Let C do the work. Python `list` indexing creates a new Python int object on every read; `bytearray` returns a C int directly.

6. **One change at a time** — Each optimization was isolated, tested (990 tests), and benchmarked independently to verify impact and catch regressions. This also makes it easy to revert any change that doesn't help.
