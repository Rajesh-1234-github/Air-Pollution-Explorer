# backend.py
from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

MODEL_NAME = "Salesforce/codegen-350M-multi"  # change if you prefer another model

print("Loading tokenizer and model (this may take a while)...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.eval()
print("Model loaded.")

@app.post("/generate")
async def generate_code(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return {"error": "No prompt provided."}

    # Give the model a small context header for better output
    input_text = f"# Language: Python\n# Task: {prompt}\n"
    inputs = tokenizer(input_text, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=200, temperature=0.2, do_sample=False)
    raw = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # remove the header we added
    code = raw.replace(input_text, "").strip()
    return {"code": code}
