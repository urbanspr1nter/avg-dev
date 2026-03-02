import { useState, useEffect, useCallback, type DragEvent } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAnnotations, uploadImage, imageUrl, type Annotation } from "./api";

const PAGE_SIZE = 20;

export default function Gallery() {
  const [page, setPage] = useState(0);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [total, setTotal] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const loadPage = useCallback(async (p: number) => {
    try {
      const data = await fetchAnnotations(p, PAGE_SIZE);
      setAnnotations(data.items ?? []);
      setTotal(data.total ?? 0);
    } catch {
      setAnnotations([]);
      setTotal(0);
    }
  }, []);

  useEffect(() => {
    loadPage(page);
  }, [page, loadPage]);

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
      for (const file of files) {
        try {
          await uploadImage(file);
        } catch {
          // skip failed
        }
      }
      setUploading(false);
      setPage(0);
      loadPage(0);
    },
    [loadPage]
  );

  return (
    <div
      className={`gallery ${dragging ? "gallery-dragover" : ""}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <h1>Annotations ({total})</h1>

      {dragging && (
        <div className="drop-overlay">
          <span>Drop JPEG images to upload</span>
        </div>
      )}

      {uploading && <div className="upload-status">Uploading...</div>}

      {annotations.length === 0 && !uploading && (
        <div className="gallery-empty">No annotations yet. Drag and drop JPEG images to get started.</div>
      )}

      <div className="gallery-grid">
        {annotations.map((ann) => (
          <div
            key={ann.id}
            className="thumbnail"
            onClick={() => navigate(`/annotation/${ann.id}`)}
          >
            <img
              className="thumbnail-img"
              src={imageUrl(ann.image_filename)}
              alt={ann.image_filename}
            />
            <div className="thumbnail-label">
              <span className="thumbnail-id">#{ann.id}</span>
              {ann.image_filename.slice(0, 8)}...
            </div>
          </div>
        ))}
      </div>

      {total > PAGE_SIZE && (
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
      )}
    </div>
  );
}
