from fastapi import FastAPI

from database import init_db

app = FastAPI(title="Pokemon Annotator API")

init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
