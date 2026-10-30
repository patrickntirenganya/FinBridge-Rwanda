"""FinBridge: evidence from NISR surveys, and farm records farmers own and lenders can read.
Run: streamlit run app.py   (Evidence pages read data/aggregates; farmer pages read only src/benchmarks.py)
"""
import streamlit as st

st.set_page_config(page_title="FinBridge", page_icon="🌱", layout="wide")

from pathlib import Path  # noqa: E402

from ui import theme as T  # noqa: E402

T.apply()

_A = Path(__file__).parent / "ui" / "assets"
st.logo(str(_A / "logo.svg"), icon_image=str(_A / "icon.svg"), size="large")
from src.i18n import LANGS, DEFAULT, t  # noqa: E402

_q = st.query_params.get("lang")
if _q in LANGS and "lang" not in st.session_state:  # landing-page links carry the chosen language
    st.session_state["lang"] = _q
st.session_state.setdefault("lang", DEFAULT)
from ui import topbar  # noqa: E402

topbar.render()  # language + light/dark, fixed top-right

from ui import about as A  # noqa: E402
from ui import farmer as F  # noqa: E402
from ui import landing as L  # noqa: E402
from ui import lender as LD  # noqa: E402

try:
    from ui import pages as P  # noqa: E402  (evidence zone: reads data/aggregates only)
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

_records = st.Page(F.my_records, title=t("nav.records"), url_path="records")
_lender = st.Page(LD.lender_view, title=t("nav.lender"), url_path="lender")
_overview = st.Page(P.overview, title=t("nav.overview"), url_path="overview")
_who = st.Page(P.who, title=t("nav.who"), url_path="who")
_opp = st.Page(P.opportunity, title=t("nav.opportunity"), url_path="opportunity")
_why = st.Page(P.why, title=t("nav.why"), url_path="why")
_social = st.Page(P.social, title=t("nav.social"), url_path="social")
_recs = st.Page(P.recommendations, title=t("nav.actions"), url_path="recommendations")
L.ROLE_PAGES.update(farmer=_records, lender=_lender, evidence=_overview)
P.LINKS.update(opportunity=_opp, who=_who, why=_why, social=_social)
L.EVIDENCE_PAGE = _overview  # target of the "See the evidence" button on Home
pg = st.navigation(expanded=True, pages={
    "": [st.Page(L.home, title=t("nav.home"), url_path="home", default=True)],
    t("nav.farmers"): [
        _records,
        st.Page(F.phone_preview, title=t("nav.ussd"), url_path="ussd"),
    ],
    t("nav.lenders"): [_lender],
    t("nav.evidence"): [
        _overview,
        _who,
        _opp,
        _social,
        _why,
        st.Page(P.farmers, title=t("nav.farmers_vs"), url_path="farmers"),
        st.Page(P.districts, title=t("nav.districts"), url_path="districts"),
        _recs,
        st.Page(P.methods, title=t("nav.methods"), url_path="methods"),
    ],
    " ": [st.Page(A.about, title=t("nav.about"), url_path="about")],
})
pg.run()
from ui import auth  # noqa: E402

auth.flush()  # hands any pending encrypted save to the browser
