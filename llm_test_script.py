import os
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_llm(model_name: str = "distilbert/distilgpt2"):
    """
    Loads and caches the model and tokenizer into memory.
    """
    print(f"Loading {model_name}...")
    device = "cpu"
    
    try:
        # Check if the path provided is a local directory
        is_local = os.path.isdir(model_name)
        
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            local_files_only=is_local
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            local_files_only=is_local
        ).to(device)
        
        # DistilGPT2 does not have a native pad token; map it to EOS token
        tokenizer.pad_token = tokenizer.eos_token
        
        print("Model loaded successfully!")
        return model, tokenizer
        
    except Exception as e:
        print("\n❌ CRITICAL ERROR: Could not load the model.")
        print(f"Details: {e}")
        print("\n💡 TROUBLESHOOTING STEP:")
        print("Your script cannot reach the internet to download the weights.")
        print("If you have downloaded the model files manually, place them in a folder")
        print("named 'distilgpt2_local' in this directory and change the execution block below to:")
        print('model, tokenizer = load_llm(model_name="./distilgpt2_local")')
        sys.exit(1)

def call_llm(prompt: str, model, tokenizer, max_new_tokens: int = 50, temperature: float = 0.7) -> str:
    """
    Sends a text prompt to the loaded DistilGPT2 model and returns the generated text response.
    """
    device = "cpu"
    
    # 1. Convert text prompt into mathematical token numbers
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    # 2. Tell the model to generate the next sequence of words
    with torch.no_grad(): # Disables gradient calculations to save your 8GB RAM
        output_tokens = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens, 
            temperature=temperature,       
            do_sample=True,                
            pad_token_id=tokenizer.pad_token_id
        )
    
    # 3. FIXED: Extract the first batch slice [0] to cleanly decode into human text
    generated_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
    return generated_text

# ==========================================
# EXECUTION EXAMPLE
# ==========================================
if __name__ == "__main__":
    # ONLINE MODE (Default)
    model, tokenizer = load_llm("distilbert/distilgpt2")
    
    # OFFLINE MODE (Uncomment below if you manually downloaded files to a folder)
    # model, tokenizer = load_llm("./distilgpt2_local")
    
    user_prompt = "The most critical factor behind the rapid economic growth of modern cities is"
    
    print(f"\nPrompt: {user_prompt}")
    print("Thinking...")
    
    response = call_llm(user_prompt, model, tokenizer, max_new_tokens=40, temperature=0.8)
    
    print("\n--- LLM Response ---")
    print(response)
    print("--------------------")
