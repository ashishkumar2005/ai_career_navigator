from __future__ import annotations

from preprocessing.text_cleaner import normalize_text


RESUME_SECTION_SIGNALS = {
    "education",
    "experience",
    "work experience",
    "professional experience",
    "internship",
    "projects",
    "project",
    "technical skills",
    "skills",
    "summary",
    "profile",
    "objective",
    "certifications",
    "achievements",
}

CONTACT_SIGNALS = {"email", "phone", "linkedin", "github", "portfolio"}

ACTION_SIGNALS = {
    "developed",
    "built",
    "created",
    "implemented",
    "managed",
    "analyzed",
    "designed",
    "optimized",
    "worked",
    "led",
}

CERTIFICATE_SIGNALS = {
    "certificate",
    "certifies",
    "certified",
    "certificate of completion",
    "certificate of achievement",
    "awarded to",
    "presented to",
    "successfully completed",
    "course completion",
    "training completion",
    "completion date",
    "credential id",
    "verify",
    "issued by",
}


def validate_resume_document(text: str, extracted_skills: list[str]) -> tuple[bool, str]:
    normalized = normalize_text(text)
    words = normalized.split()

    section_score = sum(1 for signal in RESUME_SECTION_SIGNALS if signal in normalized)
    contact_score = sum(1 for signal in CONTACT_SIGNALS if signal in normalized)
    action_score = sum(1 for signal in ACTION_SIGNALS if signal in normalized)
    certificate_score = sum(1 for signal in CERTIFICATE_SIGNALS if signal in normalized)
    skill_score = len(extracted_skills)

    if certificate_score >= 2 and section_score < 3 and action_score < 2:
        return False, "This document looks like a certificate or course completion file, not a resume. Please upload a resume/CV."

    if len(words) < 70 and not (section_score >= 3 and skill_score >= 4):
        return False, "This file does not contain enough resume content. Please upload a complete resume or paste resume text."

    if section_score < 2 and skill_score < 4:
        return False, "This document does not look like a resume. It should include sections such as skills, education, experience, or projects."

    if skill_score < 2 and action_score < 2:
        return False, "Could not find enough resume skills or work/project details. Please upload a resume/CV."

    if contact_score == 0 and section_score < 3 and action_score < 3:
        return False, "This file is missing typical resume signals. Please upload a proper resume/CV."

    return True, ""
