from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: #f7f9fc;
                color: #0f172a;
            }
            [data-testid="stSidebar"] {
                background: #ffffff;
                border-right: 1px solid #e2e8f0;
            }
            [data-testid="stSidebar"] * {
                color: #0f172a !important;
            }
            [data-testid="stSidebar"] .stRadio label {
                color: #0f172a !important;
            }
            [data-testid="stSidebar"] .stCaption {
                color: #64748b !important;
            }
            .product-header {
                background: #ffffff;
                border: 1px solid #dbe5f1;
                border-radius: 8px;
                padding: 20px 22px;
                margin-bottom: 14px;
                box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
            }
            .main-title {
                color: #0f172a;
                font-size: 2.0rem;
                font-weight: 700;
                line-height: 1.15;
                margin-bottom: 0.35rem;
            }
            .sub-title {
                color: #334155;
                font-size: 1rem;
                margin-bottom: 0.75rem;
            }
            .intro-copy {
                color: #475569;
                font-size: 0.95rem;
                margin-bottom: 0.85rem;
                max-width: 980px;
            }
            .section-title {
                font-size: 1.18rem;
                font-weight: 700;
                margin-top: 0.95rem;
                margin-bottom: 0.2rem;
                color: #0f172a;
            }
            .section-caption {
                color: #475569;
                margin-bottom: 0.9rem;
            }
            .metric-card {
                background: #ffffff;
                border: 1px solid #dbe5f1;
                border-radius: 8px;
                padding: 12px 14px 14px;
                box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
                min-height: 122px;
            }
            .metric-card.status-saudavel { border-left: 4px solid #16a34a; }
            .metric-card.status-atencao { border-left: 4px solid #f59e0b; }
            .metric-card.status-critico { border-left: 4px solid #dc2626; }
            .metric-card.status-neutro { border-left: 4px solid #334155; }
            .metric-top {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 8px;
            }
            .metric-label {
                color: #475569;
                font-size: 0.85rem;
                margin-bottom: 4px;
            }
            .metric-value {
                font-size: 1.55rem;
                font-weight: 700;
                color: #0f172a;
                line-height: 1.1;
            }
            .metric-description {
                color: #64748b;
                font-size: 0.78rem;
                line-height: 1.35;
                margin-top: 6px;
            }
            .metric-delta {
                font-size: 0.75rem;
                color: #1e40af;
                border: 1px solid #bfdbfe;
                background: #eff6ff;
                border-radius: 8px;
                padding: 2px 6px;
                white-space: nowrap;
            }
            .badge {
                display: inline-block;
                font-size: 0.78rem;
                padding: 0.18rem 0.45rem;
                border-radius: 6px;
                border: 1px solid transparent;
                margin-right: 0.2rem;
            }
            .badge-ok {background:#ecfdf5;border-color:#a7f3d0;color:#065f46;}
            .badge-warn {background:#fffbeb;border-color:#fde68a;color:#92400e;}
            .badge-bad {background:#fef2f2;border-color:#fecaca;color:#991b1b;}
            .badge-info {background:#eff6ff;border-color:#bfdbfe;color:#1e3a8a;}
            .chip {
                display: inline-block;
                background: #eef2ff;
                border: 1px solid #c7d2fe;
                border-radius: 8px;
                padding: 0.3rem 0.55rem;
                margin: 0.12rem;
                font-size: 0.82rem;
                color: #3730a3;
            }
            .insight-card {
                background: #ffffff;
                border: 1px solid #dbe5f1;
                border-radius: 8px;
                padding: 12px 14px;
                box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
                margin-bottom: 10px;
            }
            .insight-title {
                font-size: 0.92rem;
                font-weight: 700;
                color: #1e3a8a;
                margin-bottom: 6px;
            }
            .insight-item {
                color: #1f2937;
                font-size: 0.88rem;
                line-height: 1.4;
                margin-bottom: 4px;
            }
            .health-card {
                background: #ffffff;
                border: 1px solid #dbe5f1;
                border-radius: 8px;
                padding: 14px;
                box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
                margin-bottom: 12px;
            }
            .health-score {
                font-size: 2rem;
                font-weight: 800;
                color: #0f172a;
                line-height: 1;
                margin-bottom: 4px;
            }
            .health-label {
                color: #475569;
                margin-bottom: 8px;
            }
            .health-progress {
                width: 100%;
                background: #e2e8f0;
                border-radius: 8px;
                height: 8px;
                margin: 6px 0 10px;
                overflow: hidden;
            }
            .health-fill {
                height: 8px;
                border-radius: 8px;
                background: linear-gradient(90deg, #16a34a 0%, #f59e0b 65%, #dc2626 100%);
            }
            .status-panel {
                background: #ffffff;
                border: 1px solid #dbe5f1;
                border-radius: 8px;
                padding: 10px 12px;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
                margin-bottom: 10px;
            }
            .status-title {
                font-size: 0.82rem;
                color: #475569;
                margin-bottom: 2px;
            }
            .status-value {
                font-size: 0.96rem;
                font-weight: 700;
                color: #0f172a;
            }
            .cap-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 8px;
                margin-top: 6px;
            }
            .cap-card {
                background: #ffffff;
                border: 1px solid #dbe5f1;
                border-radius: 8px;
                padding: 10px 12px;
                min-height: 78px;
            }
            .cap-title {
                font-size: 0.88rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 4px;
            }
            .cap-desc {
                color: #64748b;
                font-size: 0.77rem;
                line-height: 1.35;
            }
            .product-footer {
                margin-top: 12px;
                color: #64748b;
                font-size: 0.82rem;
                text-align: center;
            }
            .stDownloadButton > button,
            .stButton > button {
                background: #0f172a !important;
                color: #ffffff !important;
                border: 1px solid #0f172a !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
            }
            .stDownloadButton > button:hover,
            .stButton > button:hover {
                background: #1e293b !important;
                color: #ffffff !important;
                border-color: #1e293b !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
