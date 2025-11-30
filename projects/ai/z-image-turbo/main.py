import torch
from diffusers import ZImagePipeline

# 1. Load the pipeline
# Use float32 for CPU execution
pipe = ZImagePipeline.from_pretrained(
    "Tongyi-MAI/Z-Image-Turbo",
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True,
)
pipe.to("cpu")

# [Optional] Attention Backend
# Diffusers uses SDPA by default. Switch to Flash Attention for better efficiency if supported:
# pipe.transformer.set_attention_backend("flash")    # Enable Flash-Attention-2
# pipe.transformer.set_attention_backend("_flash_3") # Enable Flash-Attention-3

# [Optional] Model Compilation
# Compiling the DiT model accelerates inference, but the first run will take longer to compile.
# pipe.transformer.compile()

# [Optional] CPU Offloading
# Enable CPU offloading for memory-constrained devices (requires accelerate library).
# This is not needed when running entirely on CPU.
# pipe.enable_model_cpu_offload()

prompt = "Old man and woman of Chinese descent who are husband and wife sitting on a chair looking at the camera. Around 1800s photography style. Both looked like they have worked on a farm all their lives. Detailed, black and white photograph."

# 2. Generate Image
image = pipe(
    prompt=prompt,
    height=512,
    width=512,
    num_inference_steps=14,  # This actually results in 8 DiT forwards
    guidance_scale=0.0,     # Guidance should be 0 for the Turbo models
    generator=torch.Generator("cpu").manual_seed(42),
).images[0]

image.save("example.png")

