from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: #f7f9fc;
                color: #1f2937;
            }
            .main-title {
                font-size: 2rem;
                font-weight: 700;
                line-height: 1.1;
                margin-bottom: 0.25rem;
            }
            .sub-title {
                color: #4b5563;
                font-size: 1rem;
                margin-bottom: 1.1rem;
            }
            .section-title {
                font-size: 1.2rem;
                font-weight: 700;
                margin-top: 0.6rem;
                margin-bottom: 0.1rem;
            }
            .section-caption {
                color: #6b7280;
                margin-bottom: 0.8rem;
            }
            .metric-card {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px 14px;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
                min-height: 92px;
            }
            .metric-label {
                color: #6b7280;
                font-size: 0.85rem;
                margin-bottom: 6px;
            }
            .metric-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: #111827;
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
            .chip {
                display: inline-block;
                background: #f3f4f6;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 0.3rem 0.55rem;
                margin: 0.12rem;
                font-size: 0.82rem;
            }
            .stDownloadButton > button,
            .stButton > button {
                background: #0f766e !important;
                color: #ffffff !important;
                border: 1px solid #0f766e !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
            }
            .stDownloadButton > button:hover,
            .stButton > button:hover {
                background: #0b5e58 !important;
                color: #ffffff !important;
                border-color: #0b5e58 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
