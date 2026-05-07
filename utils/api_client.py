from __future__ import annotations

import random
from datetime import datetime

import requests


FALLBACK_TRENDS = [
    "Generative AI",
    "Prompt Engineering",
    "Python",
    "SQL",
    "Cloud Security",
    "MLOps",
    "Data Visualization",
    "Vector Databases",
    "Kubernetes",
    "Power BI",
]


def get_trending_skills() -> list[str]:
    """Fetch lightweight public trend data, falling back to curated skills offline."""
    try:
        response = requests.get("https://api.github.com/search/repositories", params={"q": "machine-learning stars:>5000", "sort": "updated", "per_page": 5}, timeout=3)
        response.raise_for_status()
        topics: list[str] = []
        for item in response.json().get("items", []):
            topics.extend(item.get("topics", []))
        cleaned = [topic.replace("-", " ").title() for topic in topics if len(topic) > 2]
        if cleaned:
            return list(dict.fromkeys(cleaned))[:10]
    except Exception:
        pass

    random.seed(datetime.utcnow().strftime("%Y-%m-%d"))
    sample = FALLBACK_TRENDS[:]
    random.shuffle(sample)
    return sample[:8]

