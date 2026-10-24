"""How FinBridge works, what it is not, and where the research is."""
import streamlit as st
from src.i18n import t
from ui import theme as T

REPO = "https://github.com/patrickntirenganya/FinBridge-Rwanda"


def about():
    T.hero(t("ab.title"), t("ab.lede"), photo="farmer-beans")
    for k in ("is", "not", "privacy", "evidence", "limits"):
        st.subheader(t(f"ab.{k}_t"))
        st.markdown(t(f"ab.{k}_b"))
    st.subheader(t("ab.research_t"))
    st.markdown(t("ab.research_b") + f" [{REPO}]({REPO})")
    T.note(t("ab.draft"))
