import re
from typing import Iterable


def normalize_text(text: str) -> str:
    """Lowercase and normalize noisy text for matching."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_terms(value: str | Iterable[str]) -> list[str]:
    if isinstance(value, str):
        parts = re.split(r"[,;\n|/]+", value)
    else:
        parts = list(value)
    return [normalize_text(part) for part in parts if normalize_text(part)]


def profile_to_document(profile: dict) -> str:
    fields = [
        profile.get("skills", ""),
        profile.get("interests", ""),
        profile.get("education", ""),
        profile.get("domain", ""),
        profile.get("strengths", ""),
        profile.get("resume_text", ""),
    ]
    return normalize_text(" ".join(str(field) for field in fields if field))

