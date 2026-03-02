import { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import {
  fetchAnnotations,
  fetchAnnotation,
  updateAnnotation,
  deleteAnnotation,
  imageUrl,
  type Annotation,
  type Filters,
} from "./api";
import BoundingBoxModal from "./BoundingBoxModal";
import type { BoundingBox } from "./types";

const TASK_TYPES = [
  "bbox",
  "navigation",
];

const ACTIONS = [
  "left",
  "right",
  "up",
  "down",
  "a",
  "b",
  "start",
  "select",
  "completed",
];

export default function Detail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const filterTaskType = searchParams.get("task_type") || "";
  const filterReviewed = searchParams.get("reviewed") || "";
  const filters: Filters = {};
  if (filterTaskType) filters.task_type = filterTaskType;
  if (filterReviewed) filters.reviewed = filterReviewed;

  const filterQuery = new URLSearchParams();
  if (filterTaskType) filterQuery.set("task_type", filterTaskType);
  if (filterReviewed) filterQuery.set("reviewed", filterReviewed);
  const filterSuffix = filterQuery.toString() ? `?${filterQuery}` : "";

  const [annotation, setAnnotation] = useState<Annotation | null>(null);
  const [form, setForm] = useState<Annotation | null>(null);
  const [allIds, setAllIds] = useState<number[]>([]);
  const [saving, setSaving] = useState(false);
  const [showBoxModal, setShowBoxModal] = useState(false);

  useEffect(() => {
    fetchAnnotations(0, 10000, filters).then((data) =>
      setAllIds(data.items.map((a) => a.id))
    );
  }, [filterTaskType, filterReviewed]);

  useEffect(() => {
    const annId = Number(id);
    fetchAnnotation(annId).then((data) => {
      setAnnotation(data);
      setForm(data);
    });
  }, [id]);

  if (!form || !annotation) {
    return <div className="detail">Loading...</div>;
  }

  const index = allIds.indexOf(annotation.id);
  const hasPrev = index > 0;
  const hasNext = index < allIds.length - 1;

  const goTo = (newIndex: number) => {
    navigate(`/annotation/${allIds[newIndex]}${filterSuffix}`, { replace: true });
  };

  const updateField = (field: keyof Annotation, value: string | boolean) => {
    setForm({ ...form, [field]: value });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Minify label JSON before saving
      let labelToSave = form.label;
      try {
        labelToSave = JSON.stringify(JSON.parse(form.label));
      } catch {
        // not valid JSON, save as-is
      }

      const updated = await updateAnnotation(annotation.id, {
        system_prompt: form.system_prompt,
        instruction: form.instruction,
        label: labelToSave,
        action: form.action,
        task_type: form.task_type,
        bounding_boxes: form.bounding_boxes,
        reviewed: form.reviewed,
        validation_set: form.validation_set,
      });
      setAnnotation(updated);
      // Re-prettify label for display
      let displayLabel = updated.label;
      try {
        displayLabel = JSON.stringify(JSON.parse(updated.label), null, 2);
      } catch {
        // not JSON, keep as-is
      }
      setForm({ ...updated, label: displayLabel });
    } catch {
      // failed
    }
    setSaving(false);
  };

  const handleDelete = async () => {
    if (!confirm("Delete this annotation and its image?")) return;

    try {
      await deleteAnnotation(annotation.id);

      const newIds = allIds.filter((i) => i !== annotation.id);
      setAllIds(newIds);

      if (newIds.length === 0) {
        navigate(`/${filterSuffix}`);
      } else if (index < newIds.length) {
        navigate(`/annotation/${newIds[index]}${filterSuffix}`, { replace: true });
      } else {
        navigate(`/annotation/${newIds[newIds.length - 1]}${filterSuffix}`, { replace: true });
      }
    } catch {
      // failed
    }
  };

  return (
    <div className="detail">
      <div className="detail-nav">
        <button onClick={() => navigate(`/${filterSuffix}`)}>Back to Gallery</button>
        <span className="detail-nav-counter">
          {index >= 0 ? index + 1 : "?"} / {allIds.length}
        </span>
      </div>
      <div className="detail-content">
        <div className="detail-image">
          <div className="detail-image-container">
            <img
              className="detail-image-full"
              src={imageUrl(annotation.image_filename)}
              alt={annotation.image_filename}
            />
            {(() => {
              const boxes: BoundingBox[] = JSON.parse(form.bounding_boxes || "[]");
              if (boxes.length === 0) return null;
              return (
                <svg className="detail-image-overlay" viewBox="0 0 480 432">
                  {boxes.map((box) => (
                    <g key={box.id}>
                      <rect
                        x={box.x} y={box.y}
                        width={box.width} height={box.height}
                        fill="rgba(100, 108, 255, 0.15)"
                        stroke="#646cff"
                        strokeWidth={2}
                      />
                      <rect
                        x={box.x} y={box.y - 16}
                        width={24} height={14} rx={2}
                        fill="#646cff"
                      />
                      <text
                        x={box.x + 3} y={box.y - 5}
                        fill="#fff" fontSize={11} fontWeight={700}
                        fontFamily="'SF Mono', 'Menlo', monospace"
                      >
                        {box.id}
                      </text>
                    </g>
                  ))}
                </svg>
              );
            })()}
          </div>
          <div className="detail-filename">
            <span className="detail-id">#{annotation.id}</span>
            {annotation.image_filename}
          </div>
        </div>
        <div className="detail-form">
          <div className="form-group">
            <label>System Prompt</label>
            <textarea
              rows={3}
              value={form.system_prompt}
              onChange={(e) => updateField("system_prompt", e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Instruction</label>
            <textarea
              rows={3}
              value={form.instruction}
              onChange={(e) => updateField("instruction", e.target.value)}
            />
          </div>
          <div className="form-group">
            <div className="form-group-header">
              <label>Label</label>
              <button
                className="format-json-btn"
                onClick={() => {
                  try {
                    const parsed = JSON.parse(form.label);
                    updateField("label", JSON.stringify(parsed, null, 2));
                  } catch {
                    alert("Invalid JSON");
                  }
                }}
              >
                Format JSON
              </button>
            </div>
            <textarea
              className="mono"
              rows={6}
              value={form.label}
              onChange={(e) => updateField("label", e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Action</label>
            <select
              value={form.action}
              onChange={(e) => updateField("action", e.target.value)}
            >
              <option value="">-- Select --</option>
              {ACTIONS.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Task Type</label>
            <select
              value={form.task_type}
              onChange={(e) => updateField("task_type", e.target.value)}
            >
              <option value="">-- Select --</option>
              {TASK_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Bounding Boxes (JSON)</label>
            <pre className="mono bbox-display">{form.bounding_boxes || "[]"}</pre>
            <button className="edit-boxes-btn" onClick={() => setShowBoxModal(true)}>
              Edit Boxes
            </button>
          </div>
          <div className="form-checkboxes">
            <label>
              <input
                type="checkbox"
                checked={form.reviewed}
                onChange={(e) => updateField("reviewed", e.target.checked)}
              />
              Reviewed
            </label>
            <label>
              <input
                type="checkbox"
                checked={form.validation_set}
                onChange={(e) =>
                  updateField("validation_set", e.target.checked)
                }
              />
              Validation Set
            </label>
          </div>
          <div className="form-actions">
            <button className="delete-btn" onClick={handleDelete}>
              Delete
            </button>
            <button className="discard-btn" onClick={() => navigate(`/${filterSuffix}`)}>
              Discard
            </button>
            <button className="save-btn" onClick={handleSave} disabled={saving}>
              {saving ? "Saving..." : "Save"}
            </button>
            <div className="form-nav-arrows">
              <button disabled={!hasPrev} onClick={() => goTo(index - 1)}>
                Prev
              </button>
              <button disabled={!hasNext} onClick={() => goTo(index + 1)}>
                Next
              </button>
            </div>
          </div>
        </div>
      </div>

      {showBoxModal && (
        <BoundingBoxModal
          imageUrl={imageUrl(annotation.image_filename)}
          initialBoxes={JSON.parse(form.bounding_boxes || "[]") as BoundingBox[]}
          onSave={(boxes) => {
            updateField("bounding_boxes", JSON.stringify(boxes));
            setShowBoxModal(false);
          }}
          onCancel={() => setShowBoxModal(false)}
        />
      )}
    </div>
  );
}
