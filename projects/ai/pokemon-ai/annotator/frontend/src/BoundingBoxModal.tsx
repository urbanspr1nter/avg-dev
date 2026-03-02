import { useState, useRef, useEffect, useCallback } from "react";
import type { BoundingBox, HandlePosition, DragState } from "./types";
import "./BoundingBoxModal.css";

const IMG_W = 480;
const IMG_H = 432;
const HANDLE_SIZE = 8;
const MIN_BOX = 5;

interface Props {
  imageUrl: string;
  initialBoxes: BoundingBox[];
  onSave: (boxes: BoundingBox[]) => void;
  onCancel: () => void;
}

export default function BoundingBoxModal({ imageUrl, initialBoxes, onSave, onCancel }: Props) {
  const [boxes, setBoxes] = useState<BoundingBox[]>(initialBoxes);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [dragState, setDragState] = useState<DragState | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const nextId = useRef(
    initialBoxes.length > 0 ? Math.max(...initialBoxes.map((b) => b.id)) + 1 : 1
  );

  // Lock body scroll while modal is open
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, []);

  // Keyboard: Delete/Backspace removes selected, Escape cancels
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onCancel();
      } else if ((e.key === "Delete" || e.key === "Backspace") && selectedId !== null) {
        setBoxes((prev) => prev.filter((b) => b.id !== selectedId));
        setSelectedId(null);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [selectedId, onCancel]);

  const getSvgPoint = useCallback((e: React.MouseEvent): { x: number; y: number } => {
    const svg = svgRef.current!;
    const rect = svg.getBoundingClientRect();
    return {
      x: ((e.clientX - rect.left) / rect.width) * IMG_W,
      y: ((e.clientY - rect.top) / rect.height) * IMG_H,
    };
  }, []);

  const clamp = (val: number, min: number, max: number) => Math.max(min, Math.min(max, val));

  const deleteBox = (id: number) => {
    setBoxes((prev) => prev.filter((b) => b.id !== id));
    if (selectedId === id) setSelectedId(null);
  };

  // --- Mouse handlers ---

  const handleSvgMouseDown = (e: React.MouseEvent<SVGSVGElement>) => {
    if (e.target !== svgRef.current) return;
    const pt = getSvgPoint(e);
    setSelectedId(null);
    setDragState({ mode: "draw", startX: pt.x, startY: pt.y, currentX: pt.x, currentY: pt.y });
  };

  const handleBoxMouseDown = (e: React.MouseEvent, box: BoundingBox) => {
    e.stopPropagation();
    const pt = getSvgPoint(e);
    setSelectedId(box.id);
    setDragState({ mode: "move", boxId: box.id, offsetX: pt.x - box.x, offsetY: pt.y - box.y });
  };

  const handleHandleMouseDown = (e: React.MouseEvent, box: BoundingBox, handle: HandlePosition) => {
    e.stopPropagation();
    const pt = getSvgPoint(e);
    setDragState({ mode: "resize", boxId: box.id, handle, startBox: { ...box }, startX: pt.x, startY: pt.y });
  };

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragState) return;
    const pt = getSvgPoint(e);

    if (dragState.mode === "draw") {
      setDragState({ ...dragState, currentX: pt.x, currentY: pt.y });
    } else if (dragState.mode === "move") {
      setBoxes((prev) =>
        prev.map((b) => {
          if (b.id !== dragState.boxId) return b;
          const x = clamp(pt.x - dragState.offsetX, 0, IMG_W - b.width);
          const y = clamp(pt.y - dragState.offsetY, 0, IMG_H - b.height);
          return { ...b, x, y };
        })
      );
    } else if (dragState.mode === "resize") {
      const dx = pt.x - dragState.startX;
      const dy = pt.y - dragState.startY;
      const resized = applyResize(dragState.startBox, dragState.handle, dx, dy);
      setBoxes((prev) => prev.map((b) => (b.id === dragState.boxId ? resized : b)));
    }
  }, [dragState, getSvgPoint]);

  const handleMouseUp = useCallback(() => {
    if (!dragState) return;

    if (dragState.mode === "draw") {
      const x = Math.min(dragState.startX, dragState.currentX);
      const y = Math.min(dragState.startY, dragState.currentY);
      const w = Math.abs(dragState.currentX - dragState.startX);
      const h = Math.abs(dragState.currentY - dragState.startY);

      if (w >= MIN_BOX && h >= MIN_BOX) {
        const newBox: BoundingBox = {
          id: nextId.current++,
          x: Math.round(x),
          y: Math.round(y),
          width: Math.round(w),
          height: Math.round(h),
        };
        setBoxes((prev) => [...prev, newBox]);
        setSelectedId(newBox.id);
      }
    }

    setDragState(null);
  }, [dragState]);

  const handleSave = () => {
    const rounded = boxes.map((b) => ({
      id: b.id,
      x: Math.round(b.x),
      y: Math.round(b.y),
      width: Math.round(b.width),
      height: Math.round(b.height),
    }));
    onSave(rounded);
  };

  // --- Resize logic ---

  const renderHandles = (box: BoundingBox) => {
    const positions: { handle: HandlePosition; cx: number; cy: number }[] = [
      { handle: "nw", cx: box.x, cy: box.y },
      { handle: "n", cx: box.x + box.width / 2, cy: box.y },
      { handle: "ne", cx: box.x + box.width, cy: box.y },
      { handle: "e", cx: box.x + box.width, cy: box.y + box.height / 2 },
      { handle: "se", cx: box.x + box.width, cy: box.y + box.height },
      { handle: "s", cx: box.x + box.width / 2, cy: box.y + box.height },
      { handle: "sw", cx: box.x, cy: box.y + box.height },
      { handle: "w", cx: box.x, cy: box.y + box.height / 2 },
    ];

    return positions.map(({ handle, cx, cy }) => (
      <rect
        key={handle}
        x={cx - HANDLE_SIZE / 2}
        y={cy - HANDLE_SIZE / 2}
        width={HANDLE_SIZE}
        height={HANDLE_SIZE}
        className={`bbox-handle bbox-handle-${handle}`}
        onMouseDown={(e) => handleHandleMouseDown(e, box, handle)}
      />
    ));
  };

  // Sort so selected box renders last (on top)
  const sortedBoxes = [...boxes].sort((a, b) => {
    if (a.id === selectedId) return 1;
    if (b.id === selectedId) return -1;
    return 0;
  });

  return (
    <div className="bbox-modal-overlay" onClick={onCancel}>
      <div className="bbox-modal" onClick={(e) => e.stopPropagation()}>
        <div className="bbox-modal-header">
          <h3>Edit Bounding Boxes</h3>
          <span>{boxes.length} box{boxes.length !== 1 ? "es" : ""}</span>
        </div>
        <div className="bbox-canvas-container" style={{ width: IMG_W }}>
          <img src={imageUrl} alt="annotation" draggable={false} />
          <svg
            ref={svgRef}
            viewBox={`0 0 ${IMG_W} ${IMG_H}`}
            onMouseDown={handleSvgMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
            {sortedBoxes.map((box) => (
              <g key={box.id}>
                <rect
                  x={box.x}
                  y={box.y}
                  width={box.width}
                  height={box.height}
                  className={`bbox-rect ${selectedId === box.id ? "selected" : ""}`}
                  onMouseDown={(e) => handleBoxMouseDown(e, box)}
                />
                {/* ID label with background */}
                <rect
                  className="bbox-label-bg"
                  x={box.x}
                  y={box.y - 20}
                  width={28}
                  height={18}
                  rx={3}
                />
                <text x={box.x + 4} y={box.y - 6} className="bbox-label">
                  {box.id}
                </text>
                {/* Delete button */}
                <circle
                  cx={box.x + box.width}
                  cy={box.y}
                  r={9}
                  className="bbox-delete-circle"
                  onClick={(e) => { e.stopPropagation(); deleteBox(box.id); }}
                />
                <text
                  x={box.x + box.width}
                  y={box.y + 1}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="bbox-delete-text"
                >
                  x
                </text>
                {/* Resize handles for selected */}
                {selectedId === box.id && renderHandles(box)}
              </g>
            ))}
            {/* Drawing preview */}
            {dragState?.mode === "draw" && (
              <rect
                x={Math.min(dragState.startX, dragState.currentX)}
                y={Math.min(dragState.startY, dragState.currentY)}
                width={Math.abs(dragState.currentX - dragState.startX)}
                height={Math.abs(dragState.currentY - dragState.startY)}
                className="bbox-rect drawing"
              />
            )}
          </svg>
        </div>
        <div className="bbox-modal-footer">
          <button className="discard-btn" onClick={onCancel}>Cancel</button>
          <button className="save-btn" onClick={handleSave}>Save Boxes</button>
        </div>
      </div>
    </div>
  );
}

function applyResize(startBox: BoundingBox, handle: HandlePosition, dx: number, dy: number): BoundingBox {
  let { x, y, width, height } = startBox;

  switch (handle) {
    case "nw": x += dx; y += dy; width -= dx; height -= dy; break;
    case "n": y += dy; height -= dy; break;
    case "ne": y += dy; width += dx; height -= dy; break;
    case "e": width += dx; break;
    case "se": width += dx; height += dy; break;
    case "s": height += dy; break;
    case "sw": x += dx; width -= dx; height += dy; break;
    case "w": x += dx; width -= dx; break;
  }

  if (width < MIN_BOX) { width = MIN_BOX; }
  if (height < MIN_BOX) { height = MIN_BOX; }
  if (x < 0) { width += x; x = 0; }
  if (y < 0) { height += y; y = 0; }
  if (x + width > IMG_W) { width = IMG_W - x; }
  if (y + height > IMG_H) { height = IMG_H - y; }

  return { id: startBox.id, x: Math.round(x), y: Math.round(y), width: Math.round(width), height: Math.round(height) };
}
