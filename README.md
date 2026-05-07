# AI-Powered Career Suggestion and Resume Analysis System

A polished Streamlit application that demonstrates career recommendation, resume parsing, NLP-style skill extraction, machine learning prediction, skill gap analysis, ATS scoring, API-style trending skill integration, and downloadable PDF reports.

## Features

- Manual Career Analysis mode for skills, interests, education, domain, and strengths
- Resume Upload Analysis mode for PDF parsing and automatic profile extraction
- TF-IDF vectorization plus cosine similarity recommendation engine
- Random Forest career prediction pipeline saved with Joblib
- Career cards, readiness gauges, progress bars, Plotly charts, comparison tools, and roadmap views
- ATS-style resume score with improvement suggestions
- Trending skills panel with API fallback data
- Downloadable PDF career report

## Project Structure

```text
.
├── app.py
├── train_model.py
├── requirements.txt
├── datasets/
│   └── career_roles.csv
├── frontend/
│   └── styles.py
├── preprocessing/
│   └── text_cleaner.py
├── utils/
│   ├── api_client.py
│   ├── recommender.py
│   ├── report_generator.py
│   ├── resume_parser.py
│   └── skill_extractor.py
├── models/
│   ├── career_model.joblib
│   ├── label_encoder.joblib
│   └── tfidf_vectorizer.joblib
└── assets/
```

## Run Locally

```bash
pip install -r requirements.txt
python train_model.py
streamlit run app.py
```

If you use the bundled Codex runtime, replace `python` with the bundled Python path shown by Codex.

## Interview Talking Points

- ML: Random Forest Classifier trained from career-role data
- NLP: resume text extraction, text cleaning, skill and interest detection
- Recommendation System: TF-IDF vectors and cosine similarity
- Data Handling: Pandas/NumPy preprocessing over CSV datasets
- API Integration: trending skills request with resilient fallback
- Product Design: Streamlit dashboard with charts, cards, reports, and comparison

