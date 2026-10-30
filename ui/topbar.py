"""Top-right controls: language and light/dark theme, visible on every page.

Streamlit has no call to set its theme from Python, but it restores the viewer's choice from localStorage
(`stActiveTheme-<path>-v2` = "Light" | "Dark"). The button writes that value and reloads; the language travels in
?lang= so the reload keeps it. The bridge touches nothing else.
"""
import streamlit as st

from src.i18n import LANGS, t
from ui import theme as T

_JS = """
export default function(component) {
  const { data, parentElement } = component;
  parentElement.innerHTML = '';
  const b = document.createElement('button');
  b.type = 'button';
  b.textContent = (data.dark ? '\\u2600\\uFE0F ' : '\\u{1F319} ') + data.label;
  b.setAttribute('aria-label', data.label);
  b.style.cssText = 'font:inherit;font-size:.85rem;padding:.3rem .7rem;border-radius:999px;cursor:pointer;'
    + 'border:1px solid ' + (data.dark ? '#34483E' : '#C9D3CC') + ';'
    + 'background:' + (data.dark ? '#182922' : '#FFFFFF') + ';color:' + (data.dark ? '#E6EEE8' : '#1C2B24') + ';';
  b.onclick = () => {
    try {
      Object.keys(localStorage).filter(k => k.startsWith('stActiveTheme-')).forEach(k => localStorage.removeItem(k));
      localStorage.setItem('stActiveTheme-' + location.pathname + '-v2', JSON.stringify(data.dark ? 'Light' : 'Dark'));
      const u = new URL(location.href);
      u.searchParams.set('lang', data.lang);
      history.replaceState(null, '', u);
    } catch (e) {}
    location.reload();
  };
  parentElement.appendChild(b);
}
"""
_CSS = """<style>
.st-key-fb_topbar{position:fixed;top:.55rem;right:11rem;z-index:1000002;width:auto !important;
  display:flex;flex-direction:row !important;align-items:center;gap:.6rem}
.st-key-fb_topbar [data-testid="stElementContainer"],.st-key-fb_topbar [data-testid="stRadio"]{width:max-content !important;min-width:max-content !important;overflow:visible !important}
.st-key-fb_topbar [data-testid="stRadio"] [role="radiogroup"]{flex-direction:row !important;flex-wrap:nowrap !important;gap:.9rem}
.st-key-fb_topbar [data-testid="stRadio"] label{white-space:nowrap;margin:0}
.st-key-fb_topbar [data-testid="stRadio"] label p{font-size:.85rem}
@media (max-width:640px){.st-key-fb_topbar{right:6.5rem;gap:.3rem}}
</style>"""


def render():
    """Language radio + theme button in a fixed top-right box. Sets st.session_state['lang']."""
    st.markdown(_CSS, unsafe_allow_html=True)
    codes = list(LANGS)
    with st.container(key="fb_topbar"):
        pick = st.radio(t("lang.label"), [LANGS[c] for c in codes], horizontal=True, key="lang_pick",
                        index=codes.index(st.session_state["lang"]), label_visibility="collapsed")
        st.session_state["lang"] = codes[[LANGS[c] for c in codes].index(pick)]
        dark = T.mode() == "dark"
        try:
            st.components.v2.component("finbridge_theme", js=_JS)(
                key="fb_theme", data=dict(dark=dark, lang=st.session_state["lang"],
                                          label=t("theme.light") if dark else t("theme.dark")))
        except Exception:
            pass  # the toggle is a convenience; the Settings menu still switches theme
