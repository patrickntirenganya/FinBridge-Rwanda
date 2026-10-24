"""Landing page: a TypeScript + Tailwind bundle (frontend/) embedded as one self-contained HTML file.

All numbers are read from data/aggregates here and injected as JSON; the bundle never hard-codes a statistic.
Rebuild the bundle after editing frontend/:  cd frontend && npm run build
"""
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from src.i18n import t, lang
from ui.data import load

BUNDLE = Path(__file__).parent / "landing" / "landing.html"


def _pair(bg, ind, var, a, b, title):
    d = bg[(bg.indicator == ind) & (bg.group_var == var)].set_index("group")
    def stat(g, name):
        r = d.loc[g]
        return dict(name=t(name), est=float(r.est), lo=float(r.lo), hi=float(r.hi), n=int(r.n))
    return dict(title=t(title), a=stat(*a), b=stat(*b))


def props() -> dict:
    D = load()
    nat = D["ahs_national"].set_index("indicator")
    fd = D["fs_farmer_digital"]
    fd = fd[fd.group_var == "all"].set_index("indicator")
    seg = D["ahs_segments"].set_index("segment")
    hh = D["meta"]["ahs_weighted_households"]
    informal = seg.loc["Account, borrowed only informally"].est
    gap = nat.loc["banked_not_financed"]
    bg = D["ahs_by_group"]
    pairs = [
        _pair(bg, "loan_formal", "quintile", ("Q1 (poorest)", "home.name_Q1"), ("Q5 (richest)", "home.name_Q5"), "home.pair_wealth"),
        _pair(bg, "loan_formal", "head_sex", ("Female-headed", "home.name_F"), ("Male-headed", "home.name_M"), "home.pair_sex"),
        _pair(bg, "loan_formal", "farm_size", ("< 0.1 ha", "home.name_small"), ("> 1 ha", "home.name_big"), "home.pair_land"),
    ]
    keys = ["eyebrow", "cta_primary", "cta_secondary", "cta_lenders", "trust1", "trust2", "trust3", "card_gap", "card_phone",
            "gap_kicker", "gap_title", "gap_acct", "gap_loan", "who_kicker", "who_title", "who_body", "phone_kicker",
            "phone_title", "phone_body", "phone_smart", "phone_any", "phone_momo", "phone_cta", "ussd_label",
            "ussd1", "ussd2", "ussd3", "ussd4", "how_kicker", "how_title", "step1_t", "step1_b", "step2_t", "step2_b",
            "step3_t", "step3_b", "trust_title", "trust_1", "trust_2", "trust_3", "trust_4", "source", "credit",
            "alt_beans", "alt_field", "alt_weeding", "alt_hands", "alt_call"]
    s = {k: t(f"home.{k}") for k in keys}
    s["h1"], s["lede"] = t("hero.title"), t("hero.lede")
    s["gap_body"] = t("home.gap_body", hh=f"{hh / 1e6:.2f}", acct=f"{nat.loc['acct_formal'].est:.1f}",
                      loan=f"{nat.loc['loan_formal'].est:.1f}")
    s["gap_note"] = t("home.gap_note", gap=f"{gap.est:.1f}", lo=f"{gap.lo:.1f}", hi=f"{gap.hi:.1f}")
    q = f"?lang={lang()}"
    return dict(
        lang=lang(), s=s, pairs=pairs,
        n=dict(acct=float(nat.loc["acct_formal"].est), loan=float(nat.loc["loan_formal"].est), gap=float(gap.est),
               gapLo=float(gap.lo), gapHi=float(gap.hi), informal=float(informal),
               informalK=round(informal / 100 * hh / 1000), households=hh,
               smart=float(fd.loc["smartphone"].est), phone=float(fd.loc["own_phone"].est),
               momo=float(fd.loc["momo_registered"].est), tracks=float(fd.loc["tracks_money"].est)),
        links=dict(records="/records" + q, ussd="/ussd" + q, overview="/overview" + q, actions="/actions" + q),
    )


def home():
    if not BUNDLE.exists():
        st.error("Landing bundle missing. Run `cd frontend && npm install && npm run build`.")
        return
    st.markdown("<style>.block-container{max-width:1240px}</style>", unsafe_allow_html=True)
    # '</' inside JSON would end the script tag early
    data = json.dumps(props(), ensure_ascii=False).replace("</", "<\\/")
    components.html(BUNDLE.read_text().replace("__FB_DATA__", data), height=2600, scrolling=False)
