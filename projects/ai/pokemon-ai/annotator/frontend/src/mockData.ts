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

export const mockAnnotations: Annotation[] = Array.from({ length: 48 }, (_, i) => ({
  id: i + 1,
  image_filename: `${crypto.randomUUID()}.jpg`,
  system_prompt: "",
  instruction: "",
  label: "",
  action: "",
  task_type: "",
  bounding_boxes: "[]",
  reviewed: false,
  validation_set: false,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}));
