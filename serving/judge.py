from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Practice Judge Service")


class JudgeRequest(BaseModel):
    prompt: str = Field(min_length=1)
    response: str = Field(min_length=1)


class JudgeResult(BaseModel):
    score: float
    verdict: str
    reason: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "judge",
        "mode": "mock"
    }


@app.post("/judge", response_model=JudgeResult)
def judge(request: JudgeRequest):
    """
    Practice-only rule-based judge.
    This does not use an LLM or assess answer correctness reliably.
    """
    prompt_words = set(request.prompt.lower().split())
    response_words = set(request.response.lower().split())

    overlap = len(prompt_words & response_words)
    score = overlap / max(len(prompt_words), 1)

    return {
        "score": round(min(score, 1.0), 3),
        "verdict": "review" if score < 0.3 else "pass",
        "reason": (
            "Mock word-overlap score; not a semantic correctness evaluation."
        )
    }
