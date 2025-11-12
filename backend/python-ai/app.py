from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

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
