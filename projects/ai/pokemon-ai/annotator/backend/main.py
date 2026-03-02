from fastapi import FastAPI

app = FastAPI(title="Pokemon Annotator API")


@app.get("/health")
def health():
    return {"status": "ok"}
