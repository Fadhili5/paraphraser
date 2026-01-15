from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
from typing import Optional, Tuple, List
import threading
import torch

MODEL_NAME = "ramsrigouthamg/t5_paraphraser"

_tokenizer: Optional[PreTrainedTokenizer] = None
_model: Optional[PreTrainedModel] = None
_lock = threading.Lock()

def load_model() -> Tuple[PreTrainedTokenizer, PreTrainedModel]:
    global _tokenizer, _model

    if _tokenizer is None or _model is None:
        with _lock:
            if _tokenizer is None or _model is None:
                _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
                _model.eval()

    return _tokenizer, _model

def chunk_text(text: str, chunk_size: int=400) -> List[str]:
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = "".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks

def paraphrase_chunk(text: str) -> str:
    tokenizer, model = load_model()

    prompt = f"paraphrase: {text} </s>"
    inputs = tokenizer.encode_plus(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=256,
            num_beams=10,
            temperature=1.5,
            top_k=50,
            top_p=0.95,
            repetition_penalty=1.2,
            do_sample=True,
            early_stopping=True
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def generate_paraphrase(text: str) -> str:
    chunks = chunk_text(text)
    paraphrased_chunks = []

    for chunk in chunks:
        paraphrased_chunks.append(paraphrase_chunk(chunk))

    return "\n\n".join(paraphrased_chunks)