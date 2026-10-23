"""The app reads only the committed aggregate tables, never microdata."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st

AGG = Path(__file__).resolve().parents[1] / "data" / "aggregates"
TABLES = ["ahs_national", "ahs_by_group", "ahs_segments", "ahs_loan_sources", "ahs_loan_purpose",
          "ahs_denial_reasons", "fs_national", "fs_by_group", "fs_barriers", "fs_farmer_digital",
          "fs_records_link", "models", "validation"]

# display order for categorical groups (anything not listed keeps file order)
ORDER = {
    "quintile": ["Q1 (poorest)", "Q2", "Q3", "Q4", "Q5 (richest)"],
    "farm_size": ["< 0.1 ha", "0.1–0.3 ha", "0.3–1 ha", "> 1 ha"],
    "age_band": ["16–17", "18–30", "31–45", "46–60", "61+"],
    "education": ["No formal education", "Primary", "Secondary", "Vocational", "University / higher"],
    "farm_status": ["Farming only", "Farming + other work", "Not farming"],
    "ubudehe": ["Category 1", "Category 2", "Category 3", "Category 4", "Not yet classified"],
}


@st.cache_data
def load():
    missing = [t for t in TABLES if not (AGG / f"{t}.csv").exists()]
    if missing:
        raise FileNotFoundError(
            f"Aggregate tables missing: {missing}. Run `python pipeline/build_aggregates.py` "
            "after placing the NISR microdata in data/raw/ (see README).")
    T = {t: pd.read_csv(AGG / f"{t}.csv") for t in TABLES}
    T["meta"] = json.loads((AGG / "meta.json").read_text())
    return T


def ordered(df, group_var):
    order = ORDER.get(group_var)
    if not order:
        return df
    rank = {g: i for i, g in enumerate(order)}
    return df.assign(_r=df.group.map(rank).fillna(99)).sort_values("_r").drop(columns="_r")
