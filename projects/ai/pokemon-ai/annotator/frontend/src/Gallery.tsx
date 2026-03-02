import { useState, useCallback, type DragEvent } from "react";
import { useNavigate } from "react-router-dom";
import { mockAnnotations, type Annotation } from "./mockData";

const PAGE_SIZE = 20;
const API_BASE = "http://localhost:8000";

export default function Gallery() {
  const [page, setPage] = useState(0);
  const [annotations, setAnnotations] = useState<Annotation[]>(mockAnnotations);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const totalPages = Math.ceil(annotations.length / PAGE_SIZE);
  const start = page * PAGE_SIZE;
  const items = annotations.slice(start, start + PAGE_SIZE);

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    setDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
  }, []);

  const handleDrop = useCallback(
    async (e: DragEvent) => {
      e.preventDefault();
      setDragging(false);

      const files = Array.from(e.dataTransfer.files).filter((f) =>
        f.type.startsWith("image/jpeg")
      );

      if (files.length === 0) return;

      setUploading(true);

      const uploaded: Annotation[] = [];
      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);

        try {
          const res = await fetch(`${API_BASE}/annotations/upload`, {
            method: "POST",
            body: formData,
          });

          if (!res.ok) continue;

          const data = await res.json();
          uploaded.push({
            id: data.id,
            image_filename: data.image_filename,
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
          });
        } catch {
          // skip failed uploads
        }
      }

      if (uploaded.length > 0) {
        setAnnotations((prev) => [...uploaded, ...prev]);
        setPage(0);
      }

      setUploading(false);
    },
    []
  );

  return (
    <div
      className={`gallery ${dragging ? "gallery-dragover" : ""}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <h1>Annotations</h1>

      {dragging && (
        <div className="drop-overlay">
          <span>Drop JPEG images to upload</span>
        </div>
      )}

      {uploading && <div className="upload-status">Uploading...</div>}

      <div className="gallery-grid">
        {items.map((ann) => (
          <div
            key={ann.id}
            className="thumbnail"
            onClick={() => navigate(`/annotation/${ann.id}`)}
          >
            <div className="thumbnail-img">
              <span>{ann.id}</span>
            </div>
            <div className="thumbnail-label">{ann.image_filename.slice(0, 8)}...</div>
          </div>
        ))}
      </div>
      <div className="pagination">
        <button disabled={page === 0} onClick={() => setPage(page - 1)}>
          Prev
        </button>
        <span>
          Page {page + 1} of {totalPages}
        </span>
        <button disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}
