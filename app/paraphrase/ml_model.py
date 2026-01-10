# app/paraphrase/ml_model.py
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from typing import Optional, Tuple
import threading

MODEL_NAME = "google/flan-t5-base"

_tokenizer: Optional[AutoTokenizer] = None
_model: Optional[AutoModelForSeq2SeqLM] = None
_lock = threading.Lock()


def _load_model() -> Tuple[AutoTokenizer, AutoModelForSeq2SeqLM]:
    global _tokenizer, _model

    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        _model.eval()

    return _tokenizer, _model


def generate_paraphrase(text: str) -> str:
    tokenizer, model = _load_model()

    inputs = tokenizer(
        f"paraphrase: {text}",
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512,
    )

    outputs = model.generate(
        **inputs,
        max_length=256,
        num_beams=5,
        early_stopping=True,
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)
