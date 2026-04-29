from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
from typing import Optional, Tuple, List
import threading
import torch

MODEL_NAME = "tuner007/pegasus_paraphrase"

_tokenizer: Optional[PreTrainedTokenizer] = None
_model: Optional[PreTrainedModel] = None
_lock = threading.Lock()
_device: Optional[torch.device] = None

# Limits not to trust hugging face
MAX_MODEL_TOKENS = 60
DEFAULT_MAX_NEW_TOKENS = 128

# Safety guards
MAX_INPUT_CHARS = 3000
MAX_CHUNKS = 6

# MODE CONFIGURATION (reduced beams to save memory)
MODE_CONFIG = {
    "standard": {"prompt": "paraphrase:", "generate_args": {"num_beams": 2, "repetition_penalty": 1.2}},
    "word_changer": {"prompt": "lightly paraphrase with minimal changes:", "generate_args": {"num_beams": 2}},
    "fluency": {"prompt": "improve the fluency of:", "generate_args": {"num_beams": 2}},
    "formal": {"prompt": "rewrite in a formal tone:", "generate_args": {"num_beams": 2}},
    "academic": {"prompt": "rewrite in academic tone:", "generate_args": {"num_beams": 2}},
    "creative": {
        "prompt": "rewrite creatively:",
        "generate_args": {"do_sample": True, "top_p": 0.9, "temperature": 0.9},
    },
    "smooth": {"prompt": "make this smoother and more natural:", "generate_args": {"num_beams": 2}},
    "smarter": {"prompt": "rewrite to sound more intelligent:", "generate_args": {"num_beams": 2}},
    "shorten": {"prompt": "summarize:", "generate_args": {"num_beams": 2, "max_new_tokens": 100}},
    "expand": {"prompt": "expand and elaborate:", "generate_args": {"num_beams": 2, "max_new_tokens": 200}},
}


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


def chunk_text_by_tokens(text: str, tokenizer) -> List[str]:
    inputs = tokenizer(text, return_tensors="pt", truncation=False)
    input_ids = inputs["input_ids"][0]

    chunks = []
    for i in range(0, len(input_ids), MAX_MODEL_TOKENS):
        chunk_ids = input_ids[i: i + MAX_MODEL_TOKENS]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
        if chunk_text.strip():
            chunks.append(chunk_text)

    return chunks[:MAX_CHUNKS]


def paraphrase_chunk(text: str, mode: str, tokenizer, model, device) -> str:
    if mode not in MODE_CONFIG:
        raise ValueError(f"Invalid mode '{mode}'")

    config = MODE_CONFIG[mode]
    prompt = f"{config['prompt']} {text} </s>"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_MODEL_TOKENS,
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    extra_args = {k: v for k, v in config["generate_args"].items() if k != "max_new_tokens"}
    max_new_tokens = config["generate_args"].get("max_new_tokens", DEFAULT_MAX_NEW_TOKENS)

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=max_new_tokens,
            **extra_args,
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def generate_paraphrase(text: str, mode: str = "standard") -> str:
    if len(text) > MAX_INPUT_CHARS:
        raise ValueError("Input too long")

    tokenizer, model, device = load_model()

    chunks = chunk_text_by_tokens(text, tokenizer)

    results = []
    for chunk in chunks:
        results.append(paraphrase_chunk(chunk, mode, tokenizer, model, device))

    return "\n\n".join(results)