"""
components/download.py
----------------------
Reusable download-button helpers for filtered data exports.
"""

from __future__ import annotations

import io

import pandas as pd
import streamlit as st


def download_csv_button(
    df: pd.DataFrame,
    filename: str = "ai_talent_data.csv",
    label: str = "⬇ Download CSV",
    key: str = "dl_csv",
) -> None:
    """Render a CSV download button for *df*."""
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime="text/csv",
        key=key,
    )


def download_excel_button(
    df: pd.DataFrame,
    filename: str = "ai_talent_data.xlsx",
    label: str = "⬇ Download Excel",
    key: str = "dl_xlsx",
    sheet_name: str = "AI Jobs",
) -> None:
    """Render an Excel download button for *df*."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    st.download_button(
        label=label,
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=key,
    )
