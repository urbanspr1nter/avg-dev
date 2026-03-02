export interface BoundingBox {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
}

export type HandlePosition = "nw" | "n" | "ne" | "e" | "se" | "s" | "sw" | "w";

export type DragState =
  | { mode: "draw"; startX: number; startY: number; currentX: number; currentY: number }
  | { mode: "move"; boxId: number; offsetX: number; offsetY: number }
  | { mode: "resize"; boxId: number; handle: HandlePosition; startBox: BoundingBox; startX: number; startY: number };
