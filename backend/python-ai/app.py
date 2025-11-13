from modules.zai_reader.zai_reader import DocumentReader
from pydantic import BaseModel
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

class FolderRequest(BaseModel):
    folder_path: str

app = FastAPI(title="ZAI Python AI Service")

# allow local dashboard to call this during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "ZAI Python AI service ✅"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/embed")
def embed(query: Query):
    """
    Placeholder embed endpoint:
    Returns a tiny dummy vector (for now) to test the pipeline.
    Replace with real embedding code later (sentence-transformers etc.).
    """
    text = query.text or ""
    # dummy embedding — simple length-based vector for testing
    vector = [len(text), len(text) % 10, (len(text) * 7) % 97]
    return {"embedding": vector, "text_len": len(text)}

@app.post("/read-folder")
def read_folder(req: FolderRequest):
    reader = DocumentReader(max_file_size_mb=50)
    files = reader.scan_folder(req.folder_path)
    return {"files": files}

# ✅ New ping route
@app.get("/ping")
def ping():
    return {
        "status": "ok",
        "service": "python-ai",
        "time": datetime.utcnow().isoformat()
    }
