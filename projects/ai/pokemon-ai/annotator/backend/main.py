import uuid

from fastapi import FastAPI, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from database import DATA_DIR, get_connection, init_db

app = FastAPI(title="Pokemon Annotator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class AnnotationUpdate(BaseModel):
    system_prompt: str
    instruction: str
    label: str
    action: str
    task_type: str
    bounding_boxes: str
    reviewed: bool
    validation_set: bool


def _row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "image_filename": row["image_filename"],
        "system_prompt": row["system_prompt"],
        "instruction": row["instruction"],
        "label": row["label"],
        "action": row["action"],
        "task_type": row["task_type"],
        "bounding_boxes": row["bounding_boxes"],
        "reviewed": bool(row["reviewed"]),
        "validation_set": bool(row["validation_set"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/annotations")
def list_annotations(page: int = Query(0, ge=0), page_size: int = Query(20, ge=1, le=100)):
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) FROM annotations").fetchone()[0]
        rows = conn.execute(
            "SELECT * FROM annotations ORDER BY id DESC LIMIT ? OFFSET ?",
            (page_size, page * page_size),
        ).fetchall()
    finally:
        conn.close()

    return {
        "items": [_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@app.get("/annotations/{annotation_id}")
def get_annotation(annotation_id: int):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM annotations WHERE id = ?", (annotation_id,)
        ).fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Annotation not found")

    return _row_to_dict(row)


@app.put("/annotations/{annotation_id}")
def update_annotation(annotation_id: int, body: AnnotationUpdate):
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM annotations WHERE id = ?", (annotation_id,)
        ).fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Annotation not found")

        conn.execute(
            """UPDATE annotations SET
                system_prompt = ?, instruction = ?, label = ?, action = ?,
                task_type = ?, bounding_boxes = ?, reviewed = ?, validation_set = ?
            WHERE id = ?""",
            (
                body.system_prompt,
                body.instruction,
                body.label,
                body.action,
                body.task_type,
                body.bounding_boxes,
                int(body.reviewed),
                int(body.validation_set),
                annotation_id,
            ),
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM annotations WHERE id = ?", (annotation_id,)
        ).fetchone()
    finally:
        conn.close()

    return _row_to_dict(row)


@app.post("/annotations/upload")
async def upload_image(file: UploadFile):
    if file.content_type not in ("image/jpeg", "image/jpg"):
        raise HTTPException(status_code=400, detail="Only JPEG files are accepted")

    filename = f"{uuid.uuid4()}.jpg"
    filepath = DATA_DIR / filename

    content = await file.read()
    filepath.write_bytes(content)

    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO annotations (image_filename) VALUES (?)",
            (filename,),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM annotations WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    finally:
        conn.close()

    return _row_to_dict(row)


@app.delete("/annotations/{annotation_id}")
def delete_annotation(annotation_id: int):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT image_filename FROM annotations WHERE id = ?",
            (annotation_id,),
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Annotation not found")

        filepath = DATA_DIR / row["image_filename"]
        if filepath.exists():
            filepath.unlink()

        conn.execute("DELETE FROM annotations WHERE id = ?", (annotation_id,))
        conn.commit()
    finally:
        conn.close()

    return {"ok": True}


@app.get("/images/{filename}")
def serve_image(filename: str):
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath, media_type="image/jpeg")
