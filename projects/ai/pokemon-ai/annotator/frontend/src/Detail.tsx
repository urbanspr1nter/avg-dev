import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { mockAnnotations, type Annotation } from "./mockData";

const API_BASE = "http://localhost:8000";

export default function Detail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const index = mockAnnotations.findIndex((a) => a.id === Number(id));
  const annotation = mockAnnotations[index];

  const [form, setForm] = useState<Annotation>(
    annotation ?? mockAnnotations[0]
  );

  if (!annotation) {
    return <div className="detail">Annotation not found.</div>;
  }

  const hasPrev = index > 0;
  const hasNext = index < mockAnnotations.length - 1;

  const goTo = (newIndex: number) => {
    const next = mockAnnotations[newIndex];
    setForm(next);
    navigate(`/annotation/${next.id}`, { replace: true });
  };

  const updateField = (field: keyof Annotation, value: string | boolean) => {
    setForm({ ...form, [field]: value });
  };

  const handleDelete = async () => {
    if (!confirm("Delete this annotation and its image?")) return;

    try {
      const res = await fetch(`${API_BASE}/annotations/${annotation.id}`, {
        method: "DELETE",
      });
      if (!res.ok) return;

      mockAnnotations.splice(index, 1);

      if (mockAnnotations.length === 0) {
        navigate("/");
      } else if (index < mockAnnotations.length) {
        const next = mockAnnotations[index];
        setForm(next);
        navigate(`/annotation/${next.id}`, { replace: true });
      } else {
        const prev = mockAnnotations[index - 1];
        setForm(prev);
        navigate(`/annotation/${prev.id}`, { replace: true });
      }
    } catch {
      // failed
    }
  };

  return (
    <div className="detail">
      <div className="detail-nav">
        <button onClick={() => navigate("/")}>Back to Gallery</button>
        <span className="detail-nav-counter">
          {index + 1} / {mockAnnotations.length}
        </span>
      </div>
      <div className="detail-content">
        <div className="detail-image">
          <div className="detail-image-placeholder">
            <span>{form.id}</span>
          </div>
          <div className="detail-filename">{form.image_filename}</div>
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
            <label>Label</label>
            <textarea
              rows={3}
              value={form.label}
              onChange={(e) => updateField("label", e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Action</label>
            <input
              type="text"
              value={form.action}
              onChange={(e) => updateField("action", e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Task Type</label>
            <input
              type="text"
              value={form.task_type}
              onChange={(e) => updateField("task_type", e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Bounding Boxes (JSON)</label>
            <textarea
              rows={3}
              value={form.bounding_boxes}
              onChange={(e) => updateField("bounding_boxes", e.target.value)}
            />
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
            <button className="discard-btn" onClick={() => navigate("/")}>
              Discard
            </button>
            <button className="save-btn">Save</button>
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
    </div>
  );
}
