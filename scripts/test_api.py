import os
import httpx
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("MODEL_HOST", "127.0.0.1")
port = os.getenv("MODEL_PORT", "8014")

response = httpx.post(
    f"http://{host}:{port}/v1/chat/completions",
    json={
        "model": os.getenv("MODEL_NAME", "distilgpt2"),
        "messages": [{"role": "user", "content": "Explain ML platform engineering in one sentence."}],
        "max_tokens": 32,
    },
    timeout=120,
)
response.raise_for_status()
print(response.json())
