def inject_global_styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        :root {
            --ink: #182033;
            --muted: #667085;
            --panel: rgba(255, 255, 255, 0.92);
            --line: rgba(24, 32, 51, 0.10);
            --teal: #0f8b8d;
            --coral: #e85d75;
            --amber: #f2b84b;
            --nav: #17324a;
            --nav-2: #0f5f66;
        }
        .stApp {
            background:
                linear-gradient(90deg, rgba(15, 139, 141, .10), transparent 34%),
                linear-gradient(135deg, #f4f8fb 0%, #eaf1f7 48%, #f9fbfd 100%);
            color: var(--ink);
        }
        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: blur(10px);
        }
        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, var(--nav) 0%, #143b50 52%, var(--nav-2) 100%);
            border-right: 1px solid rgba(255,255,255,.10);
            box-shadow: 8px 0 30px rgba(24,32,51,.14);
        }
        [data-testid="stSidebar"] * {
            color: #eef7f8 !important;
        }
        [data-testid="stSidebar"] h1 {
            font-size: 1.28rem;
            line-height: 1.15;
            margin: .15rem 0 .9rem;
            padding: 1rem;
            border-radius: 8px;
            background: rgba(255,255,255,.12);
            border: 1px solid rgba(255,255,255,.22);
            box-shadow: 0 12px 26px rgba(0,0,0,.12);
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] h1:before {
            content: "AI";
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 34px;
            height: 34px;
            margin-right: .55rem;
            border-radius: 8px;
            background: #0f8b8d;
            color: #ffffff;
            font-size: .88rem;
            font-weight: 900;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            background: rgba(255, 255, 255, .10);
            border: 1px solid rgba(255, 255, 255, .16);
            border-radius: 8px;
            padding: .58rem .7rem;
            margin: .42rem 0;
            min-height: 46px;
            box-shadow: 0 8px 18px rgba(0,0,0,.08);
            transition: all .18s ease;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(255, 255, 255, .16);
            border-color: rgba(255,255,255,.28);
            transform: translateX(2px);
        }
        [data-testid="stSidebar"] [role="radiogroup"] p {
            font-size: .98rem;
            font-weight: 800;
            white-space: normal;
        }
        [data-testid="stAppViewContainer"] .main .block-container {
            max-width: 1240px;
            padding-top: 2.35rem;
            padding-bottom: 3rem;
        }
        .hero {
            position: relative;
            overflow: hidden;
            padding: 1.6rem 1.7rem;
            border: 1px solid var(--line);
            border-radius: 8px;
            background:
                linear-gradient(135deg, rgba(255,255,255,.96), rgba(255,255,255,.82)),
                linear-gradient(90deg, rgba(15,139,141,.18), rgba(232,93,117,.12));
            box-shadow: 0 18px 44px rgba(24, 32, 51, 0.10);
            margin-bottom: 1.1rem;
        }
        .hero:after {
            content: "";
            position: absolute;
            right: 0;
            top: 0;
            width: 34%;
            height: 100%;
            background: repeating-linear-gradient(135deg, rgba(15,139,141,.12), rgba(15,139,141,.12) 2px, transparent 2px, transparent 12px);
            opacity: .55;
        }
        .hero h1 {
            position: relative;
            z-index: 1;
            font-size: clamp(2rem, 4vw, 3.2rem);
            line-height: 1.06;
            margin: 0 0 .55rem 0;
            letter-spacing: 0;
            max-width: 880px;
        }
        .hero p {
            position: relative;
            z-index: 1;
            color: var(--muted);
            font-size: 1.02rem;
            margin: 0;
            max-width: 760px;
        }
        .page-title {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255,255,255,.88);
            box-shadow: 0 14px 34px rgba(24, 32, 51, 0.08);
            padding: 1.05rem 1.2rem;
            margin-bottom: 1rem;
        }
        .page-title span {
            color: var(--teal);
            font-size: .78rem;
            font-weight: 900;
            letter-spacing: .08em;
            text-transform: uppercase;
        }
        .page-title h2 {
            margin: .18rem 0 .2rem;
            font-size: 2rem;
            line-height: 1.14;
            letter-spacing: 0;
        }
        .page-title p {
            margin: 0;
            color: var(--muted);
            font-size: 1rem;
        }
        .mode-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
            margin-top: .8rem;
        }
        .home-card, .career-card, .insight-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            box-shadow: 0 12px 32px rgba(24, 32, 51, 0.08);
            padding: 1rem;
        }
        .home-card {
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .home-card h3, .career-card h3, .insight-card h3 {
            margin: 0 0 .45rem 0;
            font-size: 1.15rem;
            letter-spacing: 0;
        }
        .home-card p, .career-card p, .insight-card p {
            color: var(--muted);
            margin: .15rem 0;
        }
        .card-kicker {
            color: var(--teal);
            font-weight: 800;
            font-size: .78rem;
            text-transform: uppercase;
            letter-spacing: .08em;
        }
        .metric-row {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .85rem;
            margin: .6rem 0 1rem;
        }
        .metric-tile {
            border-radius: 8px;
            padding: .95rem;
            background: #ffffff;
            border: 1px solid var(--line);
            box-shadow: 0 10px 24px rgba(24,32,51,.07);
        }
        .metric-tile span {
            color: var(--muted);
            font-size: .82rem;
            font-weight: 700;
        }
        .metric-tile strong {
            display: block;
            margin-top: .25rem;
            font-size: 1.25rem;
        }
        .pill {
            display: inline-block;
            padding: .25rem .5rem;
            margin: .12rem;
            border-radius: 999px;
            background: rgba(15, 139, 141, .10);
            color: #0b6d6f;
            border: 1px solid rgba(15, 139, 141, .20);
            font-size: .82rem;
            font-weight: 700;
        }
        .missing {
            background: rgba(232, 93, 117, .10);
            color: #b3314d;
            border-color: rgba(232, 93, 117, .20);
        }
        .roadmap-step {
            padding: .65rem .8rem;
            margin: .42rem 0;
            border-left: 4px solid var(--teal);
            background: rgba(255,255,255,.82);
            border-radius: 4px;
            box-shadow: 0 6px 18px rgba(24,32,51,.05);
        }
        .result-panel {
            background: rgba(255,255,255,.88);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem 1.1rem;
            min-height: 220px;
            box-shadow: 0 10px 24px rgba(24,32,51,.06);
        }
        .result-panel h3 {
            margin: 0 0 .65rem;
            font-size: 1.15rem;
        }
        .form-section-title {
            color: var(--ink);
            font-size: 1.05rem;
            font-weight: 900;
            margin: .2rem 0 .7rem;
            padding-bottom: .45rem;
            border-bottom: 1px solid var(--line);
        }
        div[data-testid="stForm"] .form-section-title:not(:first-child) {
            margin-top: 1.1rem;
        }
        div[data-testid="stForm"] {
            background: rgba(255,255,255,.86);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1.35rem;
            box-shadow: 0 14px 34px rgba(24,32,51,.08);
        }
        div[data-testid="stForm"] label p {
            color: #30384a;
            font-weight: 750;
            font-size: .92rem;
        }
        div[data-testid="stForm"] textarea,
        div[data-testid="stForm"] input,
        div[data-baseweb="select"] > div {
            border-radius: 7px !important;
        }
        div[data-testid="stFileUploader"] section {
            border-radius: 8px;
            border: 1px dashed rgba(15, 139, 141, .45);
            background: rgba(255,255,255,.70);
        }
        .stButton>button, .stDownloadButton>button, div[data-testid="stFormSubmitButton"] button {
            border-radius: 6px;
            border: 1px solid rgba(15,139,141,.3);
            background: #0f8b8d;
            color: white;
            font-weight: 800;
            min-height: 42px;
        }
        .stButton>button:hover, .stDownloadButton>button:hover, div[data-testid="stFormSubmitButton"] button:hover {
            border-color: #0c7476;
            background: #0c7476;
            color: white;
        }
        @media (max-width: 760px) {
            [data-testid="stAppViewContainer"] .main .block-container { padding-top: 1.3rem; }
            .hero { padding: 1.05rem; }
            .mode-grid, .metric-row { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
