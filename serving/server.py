
import os
from functools import lru_cache

import torch
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "distilgpt2")
DEVICE = os.getenv("MODEL_DEVICE", "cpu")

app = FastAPI(title="Small Model Practice API")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = MODEL_NAME
    messages: list[Message]
    max_tokens: int = 32


@lru_cache(maxsize=1)
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

    model.to(DEVICE)
    model.eval()

    # GPT-2 models do not define a separate padding token by default.
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    return tokenizer, model


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "device": DEVICE,
    }


@app.post("/v1/chat/completions")
def chat(request: ChatRequest):
    tokenizer, model = load_model()

    user_messages = [
        message.content
        for message in request.messages
        if message.role == "user"
    ]

    prompt = user_messages[-1] if user_messages else "Hello"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    ).to(DEVICE)

    prompt_tokens = int(inputs["input_ids"].shape[1])

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max(1, min(request.max_tokens, 128)),
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_ids = outputs[0][prompt_tokens:]

    generated = tokenizer.decode(
        generated_ids,
        skip_special_tokens=True,
    ).strip()

    completion_tokens = int(generated_ids.shape[0])

    return {
        "id": "small-model-local",
        "object": "chat.completion",
        "model": MODEL_NAME,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": generated,
                },
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }
