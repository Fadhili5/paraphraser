# paraphrase/ml_model.py
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def generate_paraphrase(text: str) -> str:
    inputs = tokenizer(
        f"paraphrase: {text}",
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    outputs = model.generate(
        **inputs,
        max_length=256,
        num_beams=5,
        early_stopping=True
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)
