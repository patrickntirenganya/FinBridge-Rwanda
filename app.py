"""FinBridge Insights: banked but not financed.
Run: streamlit run app.py   (reads data/aggregates only, never microdata)
"""
import streamlit as st

st.set_page_config(page_title="FinBridge", page_icon="🌱", layout="wide")

from ui import theme as T  # noqa: E402
from ui.data import load  # noqa: E402

T.apply()
from pathlib import Path  # noqa: E402

_A = Path(__file__).parent / "ui" / "assets"
st.logo(str(_A / "logo.svg"), icon_image=str(_A / "icon.svg"), size="large")
from src.i18n import LANGS, DEFAULT, t  # noqa: E402

_q = st.query_params.get("lang")
if _q in LANGS and "lang" not in st.session_state:  # landing-page links carry the chosen language
    st.session_state["lang"] = _q
st.session_state.setdefault("lang", DEFAULT)
_codes = list(LANGS)
_pick = st.sidebar.radio(t("lang.label"), [LANGS[c] for c in _codes],
                         index=_codes.index(st.session_state["lang"]), horizontal=True, key="lang_pick")
st.session_state["lang"] = _codes[[LANGS[c] for c in _codes].index(_pick)]
try:
    load()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

from ui import pages as P  # noqa: E402

from ui import farmer as F  # noqa: E402
from ui import landing as L  # noqa: E402

pg = st.navigation({
    t("nav.home"): [st.Page(L.home, title=t("nav.home"), url_path="home", default=True)],
    t("nav.farmers"): [
        st.Page(F.my_records, title=t("nav.records"), url_path="records"),
        st.Page(F.phone_preview, title=t("nav.ussd"), url_path="ussd"),
    ],
    t("nav.evidence"): [
        st.Page(P.overview, title=t("nav.overview"), url_path="overview"),
        st.Page(F.why_records, title=t("nav.why_records"), url_path="why-records"),
        st.Page(P.who, title=t("nav.who"), url_path="who"),
        st.Page(F.adjusted, title=t("nav.adjusted"), url_path="adjusted"),
        st.Page(P.why, title=t("nav.why"), url_path="why"),
        st.Page(P.farmers, title=t("nav.farmers_vs"), url_path="farmers"),
        st.Page(P.districts, title=t("nav.districts"), url_path="districts"),
        st.Page(P.recommendations, title=t("nav.actions"), url_path="actions"),
        st.Page(P.methods, title=t("nav.methods"), url_path="methods"),
    ],
})
pg.run()
