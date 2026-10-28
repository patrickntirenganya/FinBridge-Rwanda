"""Landing page: a TypeScript + Tailwind bundle (frontend/) embedded as one self-contained HTML file.

The page carries product copy only. No survey statistic is shown anywhere in the product.
Rebuild the bundle after editing frontend/:  cd frontend && npm run build
"""
import json
from pathlib import Path

import streamlit as st

from src.i18n import t, lang

EVIDENCE_PAGE = None  # set by app.py: the st.Page that "See the evidence" opens
BUNDLE = Path(__file__).parent / "landing" / "landing.html"

KEYS = ["eyebrow", "cta_primary", "cta_secondary", "trust1", "trust2", "trust3", "card1", "card2",
        "gap_kicker", "gap_title", "gap_body", "g1_t", "g1_b", "g2_t", "g2_b", "g3_t", "g3_b",
        "f_kicker", "f_title", "f1", "f2", "f3", "f4", "l_kicker", "l_title", "l1", "l2", "l3", "l4", "l_cta",
        "phone_kicker", "phone_title", "phone_body", "phone_cta", "ussd_label", "ussd1", "ussd2", "ussd3", "ussd4",
        "how_kicker", "how_title", "step1_t", "step1_b", "step2_t", "step2_b", "step3_t", "step3_b",
        "trust_title", "trust_1", "trust_2", "trust_3", "trust_4", "cta_about", "source", "credit",
        "alt_beans", "alt_field", "alt_weeding", "alt_hands", "alt_call"]


def props() -> dict:
    s = {k: t(f"home.{k}") for k in KEYS}
    s["h1"], s["lede"] = t("hero.title"), t("hero.lede")
    q = f"?lang={lang()}"
    return dict(lang=lang(), s=s,
                links=dict(records="/records" + q, ussd="/ussd" + q, lender="/lender" + q, about="/about" + q))


def home():
    if not BUNDLE.exists():
        st.error("Landing bundle missing. Run `cd frontend && npm install && npm run build`.")
        return
    st.markdown("<style>.block-container{max-width:1240px}</style>", unsafe_allow_html=True)
    # '</' inside JSON would end the script tag early
    data = json.dumps(props(), ensure_ascii=False).replace("</", "<\\/")
    # st.iframe replaces the retired components.v1.html; height="content" fits the page to what it renders
    st.iframe(BUNDLE.read_text().replace("__FB_DATA__", data), width="stretch", height="content")

    if EVIDENCE_PAGE is not None:
        st.markdown("<style>[data-testid='stPageLink'] a{background:#2F6B4F;color:#fff !important;border-radius:12px;"
                    "padding:.85rem 1.2rem;justify-content:center;font-weight:700;font-size:1.05rem}"
                    "[data-testid='stPageLink'] a:hover{background:#245640}"
                    "[data-testid='stPageLink'] a *{color:#fff !important}</style>", unsafe_allow_html=True)
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.page_link(EVIDENCE_PAGE, label=t("home.see_evidence"), icon=":material/bar_chart:", width="stretch")
