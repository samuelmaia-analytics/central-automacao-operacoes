from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg-main: #f3f6fb;
                --surface: #ffffff;
                --border: #e2e8f0;
                --text: #0f172a;
                --muted: #475569;
                --primary: #0f4c81;
                --primary-soft: #eff6ff;
                --ok-bg: #ecfdf3;
                --ok-text: #166534;
                --warn-bg: #fff7ed;
                --warn-text: #9a3412;
                --bad-bg: #fef2f2;
                --bad-text: #b91c1c;
                --neutral-bg: #f8fafc;
                --neutral-text: #334155;
                --shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
            }
            .stApp {
                background: var(--bg-main);
                color: var(--text);
            }
            .block-container {
                padding-top: 1.6rem;
                padding-bottom: 1.6rem;
            }
            .product-header {
                background: linear-gradient(120deg, #ffffff 0%, #f8fbff 100%);
                border: 1px solid var(--border);
                border-radius: 8px;
                box-shadow: var(--shadow);
                padding: 1.2rem 1.25rem;
                margin-bottom: 1rem;
            }
            .main-title {
                font-size: 1.95rem;
                font-weight: 700;
                line-height: 1.1;
                color: #0b355a;
                margin: 0 0 0.2rem 0;
            }
            .sub-title {
                color: var(--muted);
                font-size: 1rem;
                margin: 0;
            }
            .hero-copy {
                color: var(--neutral-text);
                margin-top: 0.65rem;
                margin-bottom: 0.7rem;
                font-size: 0.92rem;
            }
            .section-title {
                font-size: 1.1rem;
                font-weight: 700;
                color: #0b355a;
                margin-top: 0.9rem;
                margin-bottom: 0.1rem;
            }
            .section-caption {
                color: var(--muted);
                margin-bottom: 0.7rem;
                font-size: 0.9rem;
            }
            .kpi-card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-left: 4px solid #cbd5e1;
                border-radius: 8px;
                padding: 0.8rem 0.85rem;
                min-height: 124px;
                box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
            }
            .kpi-title {
                color: #334155;
                font-size: 0.79rem;
                margin-bottom: 0.2rem;
                font-weight: 600;
            }
            .kpi-value {
                color: #0f172a;
                font-size: 1.55rem;
                line-height: 1.1;
                font-weight: 700;
                margin-bottom: 0.2rem;
            }
            .kpi-desc {
                color: var(--muted);
                font-size: 0.78rem;
                line-height: 1.35;
            }
            .kpi-delta {
                margin-top: 0.35rem;
                color: #334155;
                font-size: 0.75rem;
                font-weight: 600;
            }
            .kpi-saude {border-left-color: #16a34a;}
            .kpi-atencao {border-left-color: #f59e0b;}
            .kpi-critico {border-left-color: #dc2626;}
            .kpi-neutro {border-left-color: #3b82f6;}
            .badge {
                display: inline-block;
                font-size: 0.75rem;
                padding: 0.2rem 0.45rem;
                border-radius: 6px;
                border: 1px solid transparent;
                margin: 0.06rem 0.18rem 0.1rem 0;
                white-space: nowrap;
            }
            .badge-ok {background: var(--ok-bg); border-color:#bbf7d0; color: var(--ok-text);}
            .badge-warn {background: var(--warn-bg); border-color:#fed7aa; color: var(--warn-text);}
            .badge-bad {background: var(--bad-bg); border-color:#fecaca; color: var(--bad-text);}
            .badge-neutral {background: var(--neutral-bg); border-color:#e2e8f0; color: var(--neutral-text);}
            .chip {
                display: inline-block;
                background: #eef2ff;
                border: 1px solid #dbeafe;
                border-radius: 8px;
                padding: 0.22rem 0.5rem;
                margin: 0.1rem 0.18rem 0.08rem 0;
                font-size: 0.76rem;
                color: #1e3a8a;
            }
            .insight-card {
                background: #ffffff;
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 0.8rem 0.95rem;
                box-shadow: 0 1px 8px rgba(15, 23, 42, 0.04);
                margin-bottom: 0.5rem;
            }
            .insight-title {
                margin: 0 0 0.35rem 0;
                color: #0b355a;
                font-weight: 700;
                font-size: 0.95rem;
            }
            .insight-text {
                margin: 0;
                color: #334155;
                font-size: 0.86rem;
                line-height: 1.4;
            }
            .health-card {
                background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
                border: 1px solid var(--border);
                border-radius: 8px;
                box-shadow: var(--shadow);
                padding: 1rem 1.05rem;
                margin-bottom: 0.7rem;
            }
            .health-score {
                font-size: 2rem;
                line-height: 1;
                font-weight: 700;
                color: #0b355a;
                margin: 0;
            }
            .health-label {
                margin: 0.25rem 0 0.35rem 0;
                color: #334155;
                font-size: 0.88rem;
            }
            .data-source {
                background: #ffffff;
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 0.65rem 0.8rem;
                margin-bottom: 0.8rem;
            }
            .data-source-title {
                font-size: 0.78rem;
                color: #475569;
                margin-bottom: 0.15rem;
                font-weight: 600;
            }
            .data-source-line {
                font-size: 0.85rem;
                color: #0f172a;
                margin: 0;
            }
            .footer-block {
                margin-top: 0.6rem;
                border-top: 1px solid #dbe2ea;
                padding-top: 0.8rem;
                color: #475569;
                font-size: 0.78rem;
            }
            .stSidebar {
                background: #f8fafc;
            }
            .stSidebar [data-testid="stMarkdownContainer"] p {
                color: #334155;
            }
            [data-testid="stSidebar"] .stButton > button {
                width: 100%;
                background: #0f4c81 !important;
                color: #ffffff !important;
                border: 1px solid #0f4c81 !important;
                font-weight: 700 !important;
                opacity: 1 !important;
                -webkit-text-fill-color: #ffffff !important;
            }
            [data-testid="stSidebar"] .stButton > button p,
            [data-testid="stSidebar"] .stButton > button span,
            [data-testid="stSidebar"] .stButton > button div,
            [data-testid="stSidebar"] .stButton > button label,
            [data-testid="stSidebar"] .stButton > button * {
                color: #ffffff !important;
                opacity: 1 !important;
                -webkit-text-fill-color: #ffffff !important;
            }
            [data-testid="stSidebar"] .stButton > button:hover,
            [data-testid="stSidebar"] .stButton > button:focus,
            [data-testid="stSidebar"] .stButton > button:active {
                background: #0b3f6b !important;
                color: #ffffff !important;
                border: 1px solid #0b3f6b !important;
                -webkit-text-fill-color: #ffffff !important;
            }
            [data-testid="stSidebar"] .stButton > button:hover *,
            [data-testid="stSidebar"] .stButton > button:focus *,
            [data-testid="stSidebar"] .stButton > button:active * {
                color: #ffffff !important;
                opacity: 1 !important;
                -webkit-text-fill-color: #ffffff !important;
            }
            [data-testid="stSidebar"] div[data-baseweb="select"] > div,
            [data-testid="stSidebar"] div[data-baseweb="input"] > div,
            [data-testid="stSidebar"] [data-testid="stDateInput"] input,
            [data-testid="stSidebar"] [data-testid="stTextInput"] input,
            [data-testid="stSidebar"] [data-testid="stNumberInput"] input {
                background: #ffffff !important;
                color: #0f172a !important;
                border: 1px solid #cbd5e1 !important;
            }
            [data-testid="stSidebar"] div[data-baseweb="select"] input,
            [data-testid="stSidebar"] div[data-baseweb="select"] span,
            [data-testid="stSidebar"] div[data-baseweb="select"] div[role="combobox"] {
                color: #0f172a !important;
                -webkit-text-fill-color: #0f172a !important;
            }
            [data-testid="stSidebar"] div[data-baseweb="select"] input::placeholder {
                color: #64748b !important;
                opacity: 1 !important;
                -webkit-text-fill-color: #64748b !important;
            }
            [data-testid="stSidebar"] div[data-baseweb="select"] svg {
                fill: #334155 !important;
            }
            [data-testid="stSidebar"] [data-baseweb="tag"] {
                background: #e2e8f0 !important;
                color: #0f172a !important;
            }
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] .stCheckbox,
            [data-testid="stSidebar"] .stRadio,
            [data-testid="stSidebar"] .stSelectbox,
            [data-testid="stSidebar"] .stMultiSelect {
                color: #0f172a !important;
            }
            [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
            [data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {
                color: #0f172a !important;
                opacity: 1 !important;
            }
            [data-testid="stSidebar"] [data-testid="stToggle"] label {
                color: #0f172a !important;
                opacity: 1 !important;
            }
            [data-testid="stSidebar"] [data-baseweb="switch"] > div {
                background: #cbd5e1 !important;
                border: 1px solid #94a3b8 !important;
            }
            [data-testid="stSidebar"] [data-baseweb="switch"] input:checked + div {
                background: #0f4c81 !important;
                border-color: #0f4c81 !important;
            }
            [data-testid="stSidebar"] [data-baseweb="switch"] > div > div {
                background: #ffffff !important;
            }
            [data-testid="stSidebar"] [aria-disabled="true"] {
                opacity: 1 !important;
            }
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] h4,
            [data-testid="stSidebar"] h5,
            [data-testid="stSidebar"] h6 {
                color: #0b355a !important;
            }
            .stDownloadButton > button,
            .stButton > button {
                background: var(--primary) !important;
                color: #ffffff !important;
                border: 1px solid var(--primary) !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                padding: 0.4rem 0.65rem !important;
            }
            .stDownloadButton > button:hover,
            .stButton > button:hover {
                background: #0b3f6b !important;
                border-color: #0b3f6b !important;
            }
            div[data-testid="stDataFrame"] {
                border: 1px solid var(--border);
                border-radius: 8px;
                overflow: hidden;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
