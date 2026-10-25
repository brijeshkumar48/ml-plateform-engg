import os
from functools import lru_cache

from fastapi import FastAPI
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

app = FastAPI(title="Practice Embedding Service")


class EmbeddingRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=64)


@lru_cache(maxsize=1)
def load_model():
    return SentenceTransformer(MODEL_NAME, device="cpu")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "embedding",
        "model": MODEL_NAME,
        "device": "cpu",
    }


@app.post("/embeddings")
def create_embeddings(request: EmbeddingRequest):
    model = load_model()

    vectors = model.encode(
        request.texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return {
        "model": MODEL_NAME,
        "data": [
            {
                "index": index,
                "embedding": vector.tolist(),
            }
            for index, vector in enumerate(vectors)
        ],
        "dimensions": int(vectors.shape[1]),
    }
