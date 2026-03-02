import { useState, useEffect, useCallback, type DragEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { fetchAnnotations, uploadImage, imageUrl, type Annotation, type Filters } from "./api";
import type { BoundingBox } from "./types";

const PAGE_SIZE = 20;

const TASK_TYPES = ["bbox", "navigation"];

export default function Gallery() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [total, setTotal] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const page = Number(searchParams.get("page") || "0");
  const filterTaskType = searchParams.get("task_type") || "";
  const filterReviewed = searchParams.get("reviewed") || "";

  const filters: Filters = {};
  if (filterTaskType) filters.task_type = filterTaskType;
  if (filterReviewed) filters.reviewed = filterReviewed;

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const loadPage = useCallback(async (p: number, f: Filters) => {
    try {
      const data = await fetchAnnotations(p, PAGE_SIZE, f);
      setAnnotations(data.items ?? []);
      setTotal(data.total ?? 0);
    } catch {
      setAnnotations([]);
      setTotal(0);
    }
  }, []);

  useEffect(() => {
    loadPage(page, filters);
  }, [page, filterTaskType, filterReviewed, loadPage]);

  const updateParams = (updates: Record<string, string>) => {
    const next = new URLSearchParams(searchParams);
    for (const [k, v] of Object.entries(updates)) {
      if (v) next.set(k, v);
      else next.delete(k);
    }
    // Reset to page 0 when filters change
    if ("task_type" in updates || "reviewed" in updates) {
      next.set("page", "0");
    }
    setSearchParams(next);
  };

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
      updateParams({ page: "0" });
      loadPage(0, filters);
    },
    [loadPage, filters, searchParams]
  );

  // Build query string for Detail links to preserve filters
  const filterQuery = new URLSearchParams();
  if (filterTaskType) filterQuery.set("task_type", filterTaskType);
  if (filterReviewed) filterQuery.set("reviewed", filterReviewed);
  const filterSuffix = filterQuery.toString() ? `?${filterQuery}` : "";

  return (
    <div
      className={`gallery ${dragging ? "gallery-dragover" : ""}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <h1>Annotations ({total})</h1>

      <div className="gallery-filters">
        <select
          value={filterTaskType}
          onChange={(e) => updateParams({ task_type: e.target.value })}
        >
          <option value="">All Task Types</option>
          {TASK_TYPES.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <select
          value={filterReviewed}
          onChange={(e) => updateParams({ reviewed: e.target.value })}
        >
          <option value="">All</option>
          <option value="true">Reviewed</option>
          <option value="false">Unreviewed</option>
        </select>
      </div>

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
            className={`thumbnail ${ann.reviewed ? "thumbnail-reviewed" : ""}`}
            onClick={() => navigate(`/annotation/${ann.id}${filterSuffix}`)}
          >
            <div className="thumbnail-img-container">
              <img
                className="thumbnail-img"
                src={imageUrl(ann.image_filename)}
                alt={ann.image_filename}
              />
              {(() => {
                const boxes: BoundingBox[] = JSON.parse(ann.bounding_boxes || "[]");
                if (boxes.length === 0) return null;
                return (
                  <svg className="thumbnail-img-overlay" viewBox="0 0 480 432">
                    {boxes.map((box) => (
                      <rect
                        key={box.id}
                        x={box.x} y={box.y}
                        width={box.width} height={box.height}
                        fill="rgba(34, 204, 68, 0.15)"
                        stroke="#22cc44"
                        strokeWidth={6}
                      />
                    ))}
                  </svg>
                );
              })()}
            </div>
            <div className="thumbnail-label">
              <span className="thumbnail-id">#{ann.id}</span>
              {ann.image_filename.slice(0, 8)}...
            </div>
          </div>
        ))}
      </div>

      {total > PAGE_SIZE && (
        <div className="pagination">
          <button disabled={page === 0} onClick={() => updateParams({ page: String(page - 1) })}>
            Prev
          </button>
          <span>
            Page {page + 1} of {totalPages}
          </span>
          <button disabled={page >= totalPages - 1} onClick={() => updateParams({ page: String(page + 1) })}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}
