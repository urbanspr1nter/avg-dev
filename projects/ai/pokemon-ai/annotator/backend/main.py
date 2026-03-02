import uuid

from fastapi import FastAPI, HTTPException, UploadFile

from database import DATA_DIR, get_connection, init_db

app = FastAPI(title="Pokemon Annotator API")

init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


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
        annotation_id = cursor.lastrowid
    finally:
        conn.close()

    return {"id": annotation_id, "image_filename": filename}
