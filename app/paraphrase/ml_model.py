from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
from typing import Optional, Tuple, List
import threading
import torch

#MODEL_NAME = "tuner007/pegasus_paraphrase"
MODEL_NAME = "google/long-t5-tglobal-base"

_tokenizer: Optional[PreTrainedTokenizer] = None
_model: Optional[PreTrainedModel] = None
_lock = threading.Lock()
_device: Optional[torch.device] = None

def load_model() -> Tuple[PreTrainedTokenizer, PreTrainedModel, torch.device]:
    global _tokenizer, _model, _device

    if _tokenizer is None or _model is None:
        with _lock:
            if _tokenizer is None or _model is None:
                _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

                _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

                _model.to(_device)
                _model.eval()

    return _tokenizer, _model, _device

def chunk_text_by_tokens(text: str, tokenizer, model, buffer: int = 10) -> List[str]:
    max_positions = model.config.max_position_embeddings

    # Leave room for "paraphrase: " and special tokens
    safe_max_tokens = max_positions - buffer

    inputs = tokenizer(text, return_tensors="pt", tructation=False)
    input_ids = input["input_ids"][0]

    chunks = []
    for i in range(0, len(input_ids), safe_max_tokens):
        chunk_ids = input_ids[i : i + safe_max_tokens]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
        if chunk_text.strip():
            chunks.append(chunk_text)

    return chunks

def paraphrase_chunk(text: str) -> str:
    tokenizer, model, device = load_model()

    prompt = f"paraphrase: {text} </s>"
    #inputs = tokenizer.encode_plus(
    #    prompt,
    #    return_tensors="pt",
    #    truncation=True,
    #    max_length=512,
    #)
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=256,
            num_beams=5,
            #temperature=1.5,
            #top_k=50,
            #top_p=0.95,
            repetition_penalty=1.2,
            do_sample=True,
            early_stopping=True
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def generate_paraphrase(text: str) -> str:
    tokenizer, model, _ = load_model()

    chunks = chunk_text_by_tokens(text, tokenizer, model)
    paraphrased_chunks = [paraphrase_chunk(chunk) for chunk in chunks]

    return "\n\n".join(paraphrased_chunks)
