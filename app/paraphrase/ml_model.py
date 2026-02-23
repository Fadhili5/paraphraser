from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
from typing import Optional, Tuple, List
import threading
import torch

MODEL_NAME = "tuner007/pegasus_paraphrase"

_tokenizer: Optional[PreTrainedTokenizer] = None
_model: Optional[PreTrainedModel] = None
_lock = threading.Lock()
_device: Optional[torch.device] = None

# MODE CONFIGURATION
MODE_CONFIG = {
    "standard": {
        "prompt": "paraphrase:",
        "generate_args": {
            "num_beams": 5,
            "repetition_penalty": 1.2,
            "early_stopping": True,
        }
    },
    "word_changer": {
        "prompt": "lightly paraphrase with minimal changes:",
        "generate_args": {
            "num_beams": 5,
            "repetition_penalty": 1.2,
            "early_stopping": True,
        }
    },
    "fluency": {
        "prompt": "improve the fluency of:",
        "generate_args": {
            "num_beams": 5,
            "repetition_penalty": 1.2,
        }
    },
    "formal": {
        "prompt": "rewrite in a formal tone:",
        "generate_args": {
            "num_beams": 5,
        }
    },
    "academic": {
        "prompt": "rewrite in academic tone:",
        "generate_args": {
            "num_beams": 5,
        }
    },
    "creative": {
        "prompt": "rewrite creatively:",
        "generate_args": {
            "do_sample": True,
            "top_p": 0.9,
            "temperature": 0.9,
            "repetition_penalty": 1.2,
        }
    },
    "smooth": {
        "prompt": "make this smoother and more natural:",
        "generate_args": {
            "num_beams": 5,
        }
    },
    "smarter": {
        "prompt": "rewrite to sound more intelligent:",
        "generate_args": {
            "num_beams": 5,
        }
    },
    "shorten": {
        "prompt": "summarize:",
        "generate_args": {
            "num_beams": 5,
            "max_new_tokens": 120,
        }
    },
    "expand": {
        "prompt": "expand and elaborate:",
        "generate_args": {
            "num_beams": 5,
            "max_new_tokens": 400,
        }
    },
}

DEFAULT_MAX_NEW_TOKENS = 256


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


def chunk_text_by_tokens(text: str, tokenizer, model, buffer: int = 20) -> List[str]:
    max_positions = model.config.max_position_embeddings
    safe_max_tokens = max_positions - buffer

    inputs = tokenizer(text, return_tensors="pt", truncation=False)
    input_ids = inputs["input_ids"][0]

    chunks = []
    for i in range(0, len(input_ids), safe_max_tokens):
        chunk_ids = input_ids[i: i + safe_max_tokens]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
        if chunk_text.strip():
            chunks.append(chunk_text)

    return chunks


def paraphrase_chunk(text: str, mode: str) -> str:
    tokenizer, model, device = load_model()

    if mode not in MODE_CONFIG:
        raise ValueError(
            f"Invalid mode '{mode}'. Available modes: {list(MODE_CONFIG.keys())}"
        )

    config = MODE_CONFIG[mode]

    # Fix 1: Use the mode-specific prompt instead of hardcoded "paraphrase:"
    prompt = f"{config['prompt']} {text} </s>"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=model.config.max_position_embeddings,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Fix 2: Pull max_new_tokens out of generate_args before unpacking to avoid
    # duplicate keyword argument error when it appears in both places.
    extra_args = {k: v for k, v in config["generate_args"].items() if k != "max_new_tokens"}
    max_new_tokens = config["generate_args"].get("max_new_tokens", DEFAULT_MAX_NEW_TOKENS)

    generate_args = {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"],
        "max_new_tokens": max_new_tokens,
        **extra_args,
    }

    with torch.no_grad():
        outputs = model.generate(**generate_args)

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def generate_paraphrase(text: str, mode: str = "standard") -> str:
    tokenizer, model, _ = load_model()

    chunks = chunk_text_by_tokens(text, tokenizer, model)
    paraphrased_chunks = [paraphrase_chunk(chunk, mode) for chunk in chunks]

    return "\n\n".join(paraphrased_chunks)