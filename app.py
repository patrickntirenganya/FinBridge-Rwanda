"""FinBridge: farm records farmers own and lenders can read.
Run: streamlit run app.py   (no survey data is read or shown by the product)
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
_codes = list(LANGS)
_pick = st.sidebar.radio(t("lang.label"), [LANGS[c] for c in _codes],
                         index=_codes.index(st.session_state["lang"]), horizontal=True, key="lang_pick")
st.session_state["lang"] = _codes[[LANGS[c] for c in _codes].index(_pick)]

from ui import about as A  # noqa: E402
from ui import farmer as F  # noqa: E402
from ui import landing as L  # noqa: E402
from ui import lender as LD  # noqa: E402

pg = st.navigation({
    "": [st.Page(L.home, title=t("nav.home"), url_path="home", default=True)],
    t("nav.farmers"): [
        st.Page(F.my_records, title=t("nav.records"), url_path="records"),
        st.Page(F.phone_preview, title=t("nav.ussd"), url_path="ussd"),
    ],
    t("nav.lenders"): [st.Page(LD.lender_view, title=t("nav.lender"), url_path="lender")],
    t("nav.about_sec"): [st.Page(A.about, title=t("nav.about"), url_path="about")],
})
pg.run()
from ui import auth  # noqa: E402

auth.flush()  # hands any pending encrypted save to the browser
