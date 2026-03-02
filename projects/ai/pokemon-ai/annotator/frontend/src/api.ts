export const API_BASE = "http://localhost:8000";

export interface Annotation {
  id: number;
  image_filename: string;
  system_prompt: string;
  instruction: string;
  label: string;
  action: string;
  task_type: string;
  bounding_boxes: string;
  reviewed: boolean;
  validation_set: boolean;
  created_at: string;
  updated_at: string;
}

export interface AnnotationPage {
  items: Annotation[];
  total: number;
  page: number;
  page_size: number;
}

export interface Filters {
  task_type?: string;
  reviewed?: string;
}

export async function fetchAnnotations(page: number, pageSize = 20, filters: Filters = {}): Promise<AnnotationPage> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (filters.task_type) params.set("task_type", filters.task_type);
  if (filters.reviewed) params.set("reviewed", filters.reviewed);
  const res = await fetch(`${API_BASE}/annotations?${params}`);
  if (!res.ok) throw new Error("Failed to fetch annotations");
  return res.json();
}

export async function fetchAnnotation(id: number): Promise<Annotation> {
  const res = await fetch(`${API_BASE}/annotations/${id}`);
  if (!res.ok) throw new Error("Failed to fetch annotation");
  return res.json();
}

export async function updateAnnotation(id: number, data: Omit<Annotation, "id" | "image_filename" | "created_at" | "updated_at">): Promise<Annotation> {
  const res = await fetch(`${API_BASE}/annotations/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update annotation");
  return res.json();
}

export async function uploadImage(file: File): Promise<Annotation> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/annotations/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to upload image");
  return res.json();
}

export async function deleteAnnotation(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/annotations/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete annotation");
}

export function imageUrl(filename: string): string {
  return `${API_BASE}/images/${filename}`;
}
