from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from preprocessing.text_cleaner import normalize_text, profile_to_document, split_terms


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "datasets" / "career_roles.csv"
MODEL_PATH = ROOT / "models" / "career_model.joblib"
VECTORIZER_PATH = ROOT / "models" / "tfidf_vectorizer.joblib"
ENCODER_PATH = ROOT / "models" / "label_encoder.joblib"


class CareerRecommender:
    def __init__(self, dataset_path: Path = DATASET_PATH):
        self.df = pd.read_csv(dataset_path)
        self.df["document"] = self.df.apply(
            lambda row: normalize_text(
                " ".join(
                    [
                        row["career_role"],
                        row["domain"],
                        row["required_skills"],
                        row["interests"],
                        row["technologies"],
                        row["education_keywords"],
                    ]
                )
            ),
            axis=1,
        )
        self.model = joblib.load(MODEL_PATH)
        self.vectorizer = joblib.load(VECTORIZER_PATH)
        self.encoder = joblib.load(ENCODER_PATH)
        self.career_matrix = self.vectorizer.transform(self.df["document"])

    def recommend(self, profile: dict, top_n: int = 5) -> tuple[list[dict], str, float]:
        user_doc = profile_to_document(profile)
        user_vector = self.vectorizer.transform([user_doc])
        similarities = cosine_similarity(user_vector, self.career_matrix).flatten()
        prediction_index = self.model.predict(user_vector)[0]
        predicted_career = self.encoder.inverse_transform([prediction_index])[0]
        confidence = float(np.max(self.model.predict_proba(user_vector)))

        top_indices = similarities.argsort()[::-1][:top_n]
        user_terms = set(split_terms(profile.get("skills", ""))) | set(split_terms(profile.get("resume_text", "")))
        recommendations = []
        for idx in top_indices:
            row = self.df.iloc[idx]
            required = split_terms(row["required_skills"])
            technologies = split_terms(row["technologies"])
            matched = [skill for skill in required if skill in user_doc]
            missing = [skill for skill in required if skill not in user_doc][:7]
            cosine_score = similarities[idx]
            overlap_score = len(matched) / max(len(required), 1)
            match_percentage = int(round(min(98, max(35, (cosine_score * 72) + (overlap_score * 48) + 32))))
            readiness = int(round((match_percentage * 0.82) + (min(len(user_terms), 10) * 1.8)))
            recommendations.append(
                {
                    "career_role": row["career_role"],
                    "domain": row["domain"],
                    "match_percentage": match_percentage,
                    "similarity": round(float(cosine_score), 3),
                    "matched_skills": matched,
                    "missing_skills": missing,
                    "technologies": technologies,
                    "roadmap": [step.strip() for step in row["roadmap"].split(">")],
                    "readiness_score": min(readiness, 100),
                }
            )
        return recommendations, predicted_career, confidence


def calculate_ats_score(resume_text: str, extracted_skills: list[str], top_recommendation: dict | None) -> tuple[int, list[str]]:
    text = normalize_text(resume_text)
    score = 35
    suggestions: list[str] = []
    if len(text.split()) > 250:
        score += 15
    else:
        suggestions.append("Add more measurable project and responsibility details.")
    if len(extracted_skills) >= 8:
        score += 18
    else:
        suggestions.append("Include a dedicated skills section with tools, frameworks, and databases.")
    if any(token in text for token in ["project", "built", "developed", "created", "implemented"]):
        score += 12
    else:
        suggestions.append("Describe projects with action verbs and outcomes.")
    if any(char.isdigit() for char in text):
        score += 10
    else:
        suggestions.append("Add quantified results such as percentages, rankings, scale, or time saved.")
    if top_recommendation and len(top_recommendation.get("missing_skills", [])) <= 3:
        score += 10
    else:
        suggestions.append("Tailor the resume keywords toward the target career role.")
    return min(score, 100), suggestions[:5]
