import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from utils import clean_doc_text, strip_code_fences

# ─── Configuration ─────────────────────────────────────────────────────────────
LOCAL_MODEL_ID = os.getenv("LOCAL_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.3")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the Mistral tokenizer and model
_tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_ID)
_model = AutoModelForCausalLM.from_pretrained(
    LOCAL_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto"
).to(DEVICE)

# ─── Prompt Helper ──────────────────────────────────────────────────────────────
def build_prompt(doc_text: str) -> str:
    """Prepares the instruction prompt for the model."""
    cleaned = clean_doc_text(doc_text)
    system = (
        "You are a specialist in generating OpenAPI 3.0 JSON specifications.\n"
        "Provide only the JSON output, with no explanatory text.\n\n"
    )
    return system + "API Documentation:\n" + cleaned + "\n```json\n"

# ─── Generation Function ───────────────────────────────────────────────────────
def generate_spec(
    doc_text: str,
    max_new_tokens: int = 4096,
    temperature: float = 0.1
) -> str:
    """
    Generates an OpenAPI 3.0 JSON specification using a local Mistral model,
    decoding only the newly generated tokens to avoid repeating the prompt.
    """
    prompt = build_prompt(doc_text)
    inputs = _tokenizer(prompt, return_tensors="pt").to(DEVICE)
    input_ids = inputs["input_ids"]

    # Generate, returning full sequence
    outputs = _model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=False,
        eos_token_id=_tokenizer.eos_token_id,
        pad_token_id=_tokenizer.eos_token_id
    )

    # Extract only generated tokens (after prompt)
    gen_ids = outputs[0][input_ids.shape[-1]:]
    raw = _tokenizer.decode(gen_ids, skip_special_tokens=True)

    # Remove fenced markers and trailing ticks
    return strip_code_fences(raw)
