# AI-Powered Career Suggestion and Resume Analysis System

A professional Streamlit application for manual career guidance and resume-based career analysis. It demonstrates machine learning, NLP-style resume parsing, recommendation systems, ATS scoring, skill gap analysis, and downloadable PDF career reports.

## Features

- Manual Career Analysis mode for skills, interests, education, domain, experience, goals, and strengths
- Resume Upload Analysis mode with PDF parsing and resume validation
- Certificate/non-resume detection before recommendations
- TF-IDF vectorization and cosine similarity for career matching
- Random Forest classifier for career prediction
- Skill gap analysis, suggested tools, learning roadmap, readiness score, and ATS score
- Career comparison dashboard with Plotly visualizations
- Downloadable career report PDF

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
│   ├── resume_validator.py
│   └── skill_extractor.py
└── models/
    ├── career_model.joblib
    ├── label_encoder.joblib
    └── tfidf_vectorizer.joblib
```

## Run Locally

```bash
pip install -r requirements.txt
python train_model.py
streamlit run app.py
```

## Streamlit Deployment

Use `app.py` as the main file path when deploying to Streamlit Community Cloud.
