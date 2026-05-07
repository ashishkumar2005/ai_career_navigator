from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

from preprocessing.text_cleaner import normalize_text, split_terms


DATASET_PATH = Path(__file__).resolve().parents[1] / "datasets" / "career_roles.csv"

EXTRA_SKILLS = {
    "python",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "excel",
    "pivot tables",
    "vlookup",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "plotly",
    "power bi",
    "powerbi",
    "tableau",
    "dashboard development",
    "basic dashboards",
    "exploratory data analysis",
    "eda",
    "feature engineering",
    "statistical analysis",
    "data cleaning",
    "data extraction",
    "query optimization",
    "relational databases",
    "machine learning",
    "logistic regression",
    "model evaluation",
    "accuracy",
    "precision",
    "recall",
    "f1-score",
    "github",
    "git",
    "jupyter notebook",
    "jupyter",
    "vs code",
    "visual studio code",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "fastapi",
    "django",
    "flask",
    "react",
    "nodejs",
    "typescript",
    "javascript",
    "html",
    "css",
    "selenium",
    "playwright",
    "postman",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "linux",
    "airflow",
    "spark",
    "snowflake",
    "dbt",
}


def load_skill_vocabulary(dataset_path: Path = DATASET_PATH) -> list[str]:
    df = pd.read_csv(dataset_path)
    vocab: set[str] = set()
    for column in ["required_skills", "technologies", "interests"]:
        for value in df[column].fillna(""):
            vocab.update(split_terms(value))
    vocab.update(EXTRA_SKILLS)
    aliases = {
        "node.js": "nodejs",
        "node js": "nodejs",
        "powerbi": "power bi",
        "power-bi": "power bi",
        "ms sql": "sql server",
        "ms-sql": "sql server",
        "jupyter notebooks": "jupyter notebook",
        "vscode": "vs code",
        "visual studio code": "vs code",
        "github": "git",
        "ci/cd": "ci cd",
        "rest": "rest api",
        "apis": "api development",
        "llm": "llms",
    }
    vocab.update(aliases.keys())
    vocab.update(aliases.values())
    return sorted(vocab, key=len, reverse=True)


def extract_keywords(text: str, vocabulary: list[str] | None = None) -> list[str]:
    normalized = f" {normalize_text(text)} "
    vocabulary = vocabulary or load_skill_vocabulary()
    found: list[str] = []
    for term in vocabulary:
        normalized_term = normalize_text(term)
        needle = f" {normalized_term} "
        compact_text = normalized.replace(" ", "").replace("-", "")
        compact_term = normalized_term.replace(" ", "").replace("-", "")
        compact_match = len(compact_term) > 1 and compact_term in compact_text
        if needle in normalized or compact_match:
            found.append(_canonical_skill(term))
    return sorted(set(found))


def _canonical_skill(term: str) -> str:
    canonical = {
        "powerbi": "power bi",
        "power-bi": "power bi",
        "visual studio code": "vs code",
        "vscode": "vs code",
        "jupyter notebooks": "jupyter notebook",
    }
    return canonical.get(normalize_text(term), normalize_text(term))


def infer_interests(text: str) -> list[str]:
    interests = extract_keywords(text)
    normalized = normalize_text(text)
    soft_signals = {
        "leadership": ["led", "managed", "coordinated", "stakeholder"],
        "research": ["research", "experiment", "survey", "paper"],
        "analytics": ["dashboard", "insight", "metric", "report"],
        "automation": ["automated", "workflow", "script", "pipeline"],
        "design": ["prototype", "wireframe", "usability", "visual"],
    }
    for label, tokens in soft_signals.items():
        if any(token in normalized for token in tokens):
            interests.append(label)
    return sorted(set(interests))


def top_keyword_counts(text: str, limit: int = 12) -> dict[str, int]:
    normalized = normalize_text(text)
    words = [word for word in normalized.split() if len(word) > 3]
    stop_words = {"with", "from", "this", "that", "have", "using", "will", "and", "the"}
    counts = Counter(word for word in words if word not in stop_words)
    return dict(counts.most_common(limit))
