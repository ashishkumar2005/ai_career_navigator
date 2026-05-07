from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from preprocessing.text_cleaner import normalize_text


ROOT = Path(__file__).resolve().parent
DATASET_PATH = ROOT / "datasets" / "career_roles.csv"
MODEL_DIR = ROOT / "models"


def build_training_rows(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    documents: list[str] = []
    labels: list[str] = []
    for _, row in df.iterrows():
        base = " ".join(
            [
                row["career_role"],
                row["domain"],
                row["required_skills"],
                row["interests"],
                row["technologies"],
                row["education_keywords"],
            ]
        )
        variants = [
            base,
            f"{row['required_skills']} {row['interests']}",
            f"{row['technologies']} {row['domain']} {row['education_keywords']}",
            f"I like {row['interests']} and know {row['required_skills']}",
        ]
        for variant in variants:
            documents.append(normalize_text(variant))
            labels.append(row["career_role"])
    return documents, labels


def train() -> None:
    MODEL_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATASET_PATH)
    documents, labels = build_training_rows(df)
    encoder = LabelEncoder()
    y = encoder.fit_transform(labels)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=1800)
    X = vectorizer.fit_transform(documents)
    model = RandomForestClassifier(n_estimators=220, random_state=42, class_weight="balanced")
    model.fit(X, y)

    joblib.dump(model, MODEL_DIR / "career_model.joblib")
    joblib.dump(vectorizer, MODEL_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(encoder, MODEL_DIR / "label_encoder.joblib")
    print(f"Saved model artifacts to {MODEL_DIR}")


if __name__ == "__main__":
    train()

