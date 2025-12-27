from fastapi import FastAPI

app = FastAPI(title="SOP RAG API")

@app.get("/")
def health():
    return {"status": "ok", "message": "SOP RAG backend running"}
