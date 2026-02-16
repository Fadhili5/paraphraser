from pydantic import BaseModel, Field
from typing import Literal

AllowedModes = Literal[
    "standard",
    "word_changer",
    "fluency",
    "formal",
    "academic",
    "creative",
    "smooth",
    "smarter",
    "shorten",
    "expand",
]

class ParaphraseRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    mode: AllowedModes = "standard"

class ParaphraseResponse(BaseModel):
    paraphrased_text: str
    original_length: int
    paraphrased_length: int