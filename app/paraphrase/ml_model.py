# app/paraphrase/ml_model.py
import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROP_API_KEY)

MAX_INPUT_CHARS = 3000

MODE_PROMPTS = {
    "standard":     "Paraphrase the following text. Return only the paraphrased text, nothing else.",
    "word_changer": "Lightly paraphrase the following text with minimal changes. Return only the result.",
    "fluency":      "Improve the fluency of the following text. Return only the result.",
    "formal":       "Rewrite the following text in a formal tone. Return only the result.",
    "academic":     "Rewrite the following text in an academic tone. Return only the result.",
    "creative":     "Rewrite the following text creatively. Return only the result.",
    "smooth":       "Make the following text smoother and more natural. Return only the result.",
    "smarter":      "Rewrite the following text to sound more intelligent. Return only the result.",
    "shorten":      "Summarize the following text concisely. Return only the result.",
    "expand":       "Expand and elaborate on the following text. Return only the result.",
}

def generate_paraphrase(text: str, mode: str = "standard") -> str:
    if len(text) > MAX_INPUT_CHARS:
        raise ValueError("Input too long")
    if mode not in MODE_PROMPTS:
        raise ValueError(f"Invalid mode '{mode}'")

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=MODE_PROMPTS[mode],
        messages=[
            {"role": "user", "content": text}
        ],
    )
    return message.content[0].text
