import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  fetchAnnotations,
  fetchAnnotation,
  updateAnnotation,
  deleteAnnotation,
  imageUrl,
  type Annotation,
} from "./api";

export default function Detail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [annotation, setAnnotation] = useState<Annotation | null>(null);
  const [form, setForm] = useState<Annotation | null>(null);
  const [allIds, setAllIds] = useState<number[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchAnnotations(0, 10000).then((data) =>
      setAllIds(data.items.map((a) => a.id))
    );
  }, []);

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
    navigate(`/annotation/${allIds[newIndex]}`, { replace: true });
  };

  const updateField = (field: keyof Annotation, value: string | boolean) => {
    setForm({ ...form, [field]: value });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await updateAnnotation(annotation.id, {
        system_prompt: form.system_prompt,
        instruction: form.instruction,
        label: form.label,
        action: form.action,
        task_type: form.task_type,
        bounding_boxes: form.bounding_boxes,
        reviewed: form.reviewed,
        validation_set: form.validation_set,
      });
      setAnnotation(updated);
      setForm(updated);
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
        navigate("/");
      } else if (index < newIds.length) {
        navigate(`/annotation/${newIds[index]}`, { replace: true });
      } else {
        navigate(`/annotation/${newIds[newIds.length - 1]}`, { replace: true });
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
          {index >= 0 ? index + 1 : "?"} / {allIds.length}
        </span>
      </div>
      <div className="detail-content">
        <div className="detail-image">
          <img
            className="detail-image-full"
            src={imageUrl(annotation.image_filename)}
            alt={annotation.image_filename}
          />
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
            <label>Label</label>
            <textarea
              className="mono"
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
              className="mono"
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
    </div>
  );
}
