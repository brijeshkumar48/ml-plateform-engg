import ast
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Practice Code Sandbox API")


class SandboxRequest(BaseModel):
    code: str = Field(min_length=1, max_length=10000)
    language: Literal["python"] = "python"


class SandboxResponse(BaseModel):
    status: str
    language: str
    validated: bool
    message: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "sandbox",
        "mode": "validation-only",
        "execution_enabled": False,
    }


@app.post("/execute", response_model=SandboxResponse)
def validate_code(request: SandboxRequest):
    """
    Practice-only validation endpoint.
    Parses Python syntax but never executes submitted code.
    """
    try:
        ast.parse(request.code)
    except SyntaxError as exc:
        return {
            "status": "invalid",
            "language": request.language,
            "validated": False,
            "message": (
                f"Syntax error on line {exc.lineno}: {exc.msg}"
            ),
        }

    return {
        "status": "validated",
        "language": request.language,
        "validated": True,
        "message": (
            "Python syntax is valid. Code was not executed."
        ),
    }
