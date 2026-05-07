from __future__ import annotations
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from frontend.styles import inject_global_styles
from train_model import train
from utils.recommender import CareerRecommender, calculate_ats_score
from utils.report_generator import build_pdf_report
from utils.resume_parser import extract_text_from_pdf
from utils.resume_validator import validate_resume_document
from utils.skill_extractor import extract_keywords, infer_interests


ROOT = Path(__file__).resolve().parent
MODEL_FILES = [ROOT / "models" / name for name in ["career_model.joblib", "tfidf_vectorizer.joblib", "label_encoder.joblib"]]

DOMAIN_OPTIONS = [
    "Data Science",
    "Data Analytics",
    "Data Engineering",
    "Artificial Intelligence",
    "Generative AI",
    "Machine Learning",
    "Software Engineering",
    "Frontend Development",
    "Backend Development",
    "Full Stack Development",
    "Mobile App Development",
    "Cloud Computing",
    "DevOps",
    "Cybersecurity",
    "Networking",
    "Database Management",
    "Business Intelligence",
    "Product Management",
    "UI/UX Design",
    "Quality Assurance",
    "Blockchain",
    "Internet of Things",
    "Robotics",
    "Digital Marketing",
    "Finance Analytics",
    "Healthcare Analytics",
    "Education Technology",
    "Game Development",
    "AR/VR",
    "Human Resources Analytics",
]

st.set_page_config(page_title="AI Career Navigator", page_icon="AI", layout="wide", initial_sidebar_state="expanded")
inject_global_styles()


@st.cache_resource(show_spinner=False)
def get_recommender(model_stamp: float) -> CareerRecommender:
    if not all(path.exists() for path in MODEL_FILES):
        train()
    return CareerRecommender()


def model_stamp() -> float:
    existing = [path.stat().st_mtime for path in MODEL_FILES if path.exists()]
    dataset = ROOT / "datasets" / "career_roles.csv"
    existing.append(dataset.stat().st_mtime)
    return max(existing)


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="card-kicker">Career Intelligence Dashboard</div>
            <h1>AI-Powered Career Suggestion and Resume Analysis System</h1>
            <p>Analyze skills, education, interests, and resume signals to discover role fit, ATS readiness, skill gaps, technologies, and a practical roadmap.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-title">
            <div>
                <span>AI Career Navigator</span>
                <h2>{title}</h2>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home(mode: str) -> None:
    hero()
    st.markdown(
        """
        <div class="mode-grid">
            <div class="home-card">
                <div>
                    <div class="card-kicker">Mode 01</div>
                    <h3>Manual Career Analysis</h3>
                    <p>Enter skills, interests, education, domain preference, and strengths. The engine combines TF-IDF similarity with Random Forest prediction to rank careers.</p>
                </div>
                <p><b>Output:</b> matches, missing skills, tools, readiness score, roadmap, and PDF report.</p>
            </div>
            <div class="home-card">
                <div>
                    <div class="card-kicker">Mode 02</div>
                    <h3>Resume Analysis</h3>
                    <p>Upload a resume PDF or paste resume text. The app extracts career signals, calculates ATS readiness, and recommends suitable paths.</p>
                </div>
                <p><b>Output:</b> extracted skills, role fit, ATS score, improvement tips, and comparison dashboard.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def profile_form() -> dict:
    with st.form("manual_profile_form"):
        st.markdown('<div class="form-section-title">Profile Details</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        with p1:
            education = st.text_input("Education Background", placeholder="B.Tech CSE, BCA, MBA, Statistics, Diploma")
            experience = st.selectbox("Experience Level", ["Student / Fresher", "0-1 years", "1-3 years", "3-5 years", "5+ years"])
        with p2:
            domain = st.selectbox(
                "Preferred Domain",
                DOMAIN_OPTIONS,
            )
            goal = st.selectbox("Career Goal", ["Get first job", "Switch domain", "Upskill for promotion", "Build portfolio", "Prepare for interviews"])

        st.markdown('<div class="form-section-title">Skills and Preferences</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        with s1:
            skills = st.text_area("Technical Skills", placeholder="Python, SQL, Pandas, Power BI, GitHub, Excel", height=150)
        with s2:
            interests = st.text_area("Career Interests", placeholder="AI, analytics, dashboards, products, cloud, security", height=150)
        strengths = st.text_area("Strengths", placeholder="Problem solving, communication, leadership, research, teamwork", height=105)

        submitted = st.form_submit_button("Analyze Career Fit")
    if not submitted:
        return {}
    return {"skills": skills, "interests": interests, "education": education, "domain": domain, "strengths": strengths, "experience": experience, "goal": goal}


def score_gauge(label: str, value: int) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": label},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0f8b8d"},
                "steps": [
                    {"range": [0, 45], "color": "#f8d7da"},
                    {"range": [45, 75], "color": "#fff3cd"},
                    {"range": [75, 100], "color": "#d1e7dd"},
                ],
            },
        )
    )
    fig.update_layout(height=245, margin=dict(l=20, r=20, t=45, b=10))
    return fig


def render_recommendations(profile: dict, recommendations: list[dict], predicted: str, confidence: float, ats_score: int | None = None, suggestions: list[str] | None = None) -> None:
    top = recommendations[0]
    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-tile"><span>Top Career Match</span><strong>{top['career_role']}</strong></div>
            <div class="metric-tile"><span>ML Prediction</span><strong>{predicted}</strong><p>{confidence:.0%} confidence</p></div>
            <div class="metric-tile"><span>Career Readiness</span><strong>{top['readiness_score']}%</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_df = pd.DataFrame(recommendations)
    fig = px.bar(chart_df, x="match_percentage", y="career_role", orientation="h", color="domain", text="match_percentage", title="Career Match Percentage")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=380, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)

    if ats_score is not None:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.plotly_chart(score_gauge("ATS Resume Score", ats_score), use_container_width=True)
        with c2:
            st.markdown('<div class="result-panel"><h3>Resume Improvements</h3>', unsafe_allow_html=True)
            for item in suggestions or []:
                st.write(f"- {item}")
            st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Recommended Career Paths")
    for rec in recommendations:
        st.markdown(
            f"""
            <div class="career-card">
                <h3>{rec['career_role']} <span style="float:right;color:#0f8b8d;">{rec['match_percentage']}%</span></h3>
                <p><b>Domain:</b> {rec['domain']} | <b>Readiness:</b> {rec['readiness_score']}%</p>
                <p><b>Suggested technologies/tools:</b></p>
                {''.join(f'<span class="pill">{tool}</span>' for tool in rec['technologies'][:8])}
                <p style="margin-top:.8rem;"><b>Missing skills:</b></p>
                {''.join(f'<span class="pill missing">{skill}</span>' for skill in rec['missing_skills']) or '<span class="pill">No major gaps</span>'}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(rec["match_percentage"] / 100)

    st.subheader("Personalized Learning Roadmap")
    for index, step in enumerate(top["roadmap"], start=1):
        st.markdown(f'<div class="roadmap-step"><b>Step {index}:</b> {step}</div>', unsafe_allow_html=True)

    st.subheader("Career Comparison")
    options = [rec["career_role"] for rec in recommendations]
    selected = st.multiselect("Compare careers", options, default=options[:2], max_selections=3)
    if selected:
        compare_df = chart_df[chart_df["career_role"].isin(selected)][["career_role", "match_percentage", "readiness_score", "domain"]]
        st.dataframe(compare_df, use_container_width=True, hide_index=True)

    insights = {
        "top_match": top["career_role"],
        "readiness_score": f"{top['readiness_score']}%",
        "next_focus": ", ".join(top["missing_skills"][:3]) or "portfolio depth",
    }
    pdf_bytes = build_pdf_report("AI Career Analysis Report", profile, recommendations, insights)
    render_report_download(pdf_bytes)


def render_report_download(pdf_bytes: bytes) -> None:
    st.download_button(
        "Download Career Report PDF",
        data=pdf_bytes,
        file_name="career_analysis_report.pdf",
        mime="application/pdf",
        key="career_report_download",
    )


def manual_mode() -> None:
    page_header("Manual Career Analysis", "Enter your profile details and get career matches, skill gaps, and a learning roadmap.")
    profile = profile_form()
    if not profile:
        st.caption("Fill the profile form and run the analysis.")
        return
    recommender = get_recommender(model_stamp())
    recommendations, predicted, confidence = recommender.recommend(profile)
    render_recommendations(profile, recommendations, predicted, confidence)


def resume_mode() -> None:
    page_header("Resume Upload Analysis", "Upload your resume PDF. If the file is scanned, paste the resume text in the fallback box.")
    upload_col, paste_col = st.columns([1, 1])
    with upload_col:
        uploaded = st.file_uploader("Upload resume PDF", type=["pdf"])
    with paste_col:
        pasted_text = st.text_area("Optional resume text fallback", placeholder="If your PDF is scanned or locked, paste resume text here.", height=145)

    if not uploaded and not pasted_text.strip():
        st.caption("Upload a PDF resume or paste resume text to begin.")
        return

    resume_text = pasted_text.strip()
    try:
        if uploaded:
            extracted = extract_text_from_pdf(uploaded)
            if extracted.strip():
                resume_text = extracted
    except ValueError as exc:
        if not resume_text:
            st.warning(f"{exc} Paste the resume text in the fallback box and the analysis will still work.")
            return
        st.info("Using the pasted resume text because the PDF did not expose readable text.")

    if len(resume_text.split()) < 25:
        st.warning("The extracted text looks very short. Add/paste more resume content for better recommendations.")
        return

    extracted_skills = extract_keywords(resume_text)
    is_resume, validation_message = validate_resume_document(resume_text, extracted_skills)
    if not is_resume:
        st.error(validation_message)
        return

    inferred_interests = infer_interests(resume_text)
    profile = {
        "skills": ", ".join(extracted_skills),
        "interests": ", ".join(inferred_interests),
        "education": "Extracted from resume",
        "domain": "",
        "strengths": "",
        "resume_text": resume_text,
    }
    recommender = get_recommender(model_stamp())
    recommendations, predicted, confidence = recommender.recommend(profile)
    ats_score, suggestions = calculate_ats_score(resume_text, extracted_skills, recommendations[0])

    if not extracted_skills:
        st.warning("The resume was read, but no known technical skills were detected. Try pasting the skills section in the fallback box for better results.")

    render_recommendations(profile, recommendations, predicted, confidence, ats_score, suggestions)


def main() -> None:
    st.sidebar.title("AI Career Navigator")
    st.sidebar.caption("Choose one section")
    mode = st.sidebar.radio("Navigation", ["Home", "Manual Career Analysis", "Resume Upload Analysis"], label_visibility="collapsed")

    if mode == "Home":
        render_home(mode)
    elif mode == "Manual Career Analysis":
        manual_mode()
    else:
        resume_mode()


if __name__ == "__main__":
    main()
