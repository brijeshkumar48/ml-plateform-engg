from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Practice Reward Service")


class RewardRequest(BaseModel):
    prompt: str = Field(min_length=1)
    response: str = Field(min_length=1)


class RewardResult(BaseModel):
    reward: float
    details: dict


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "reward",
        "mode": "mock"
    }


@app.post("/score", response_model=RewardResult)
def score_response(request: RewardRequest):
    """
    Practice-only heuristic reward.
    This is not a trained reward model and does not measure
    semantic correctness or human preference reliably.
    """
    prompt_words = set(request.prompt.lower().split())
    response_words = set(request.response.lower().split())

    # Basic response-quality signals.
    length_score = min(len(response_words) / 20.0, 1.0)
    relevance_score = (
        len(prompt_words & response_words) / max(len(prompt_words), 1)
    )

    # Weighted mock reward in the range 0.0 to 1.0.
    reward = (0.4 * length_score) + (0.6 * relevance_score)
    reward = max(0.0, min(reward, 1.0))

    return {
        "reward": round(reward, 3),
        "details": {
            "mode": "mock",
            "length_score": round(length_score, 3),
            "word_overlap_score": round(relevance_score, 3),
            "note": "Heuristic demo only; not a trained reward model."
        }
    }
