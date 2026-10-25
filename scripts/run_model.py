import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM

load_dotenv()
model_name = os.getenv("MODEL_NAME", "distilgpt2")
device = os.getenv("MODEL_DEVICE", "cpu")

print(f"Loading model: {model_name}")
print(f"Device: {device}")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.to(device)
model.eval()

prompt = "Machine learning platform engineering means"
inputs = tokenizer(prompt, return_tensors="pt").to(device)


outputs = model.generate(
    **inputs,
    max_new_tokens=60,
    do_sample=True,
    temperature=0.8,
    top_p=0.9,
    repetition_penalty=1.2,
    pad_token_id=tokenizer.eos_token_id,
)

result = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True,
)

print("\nGenerated output:")
print(result)

