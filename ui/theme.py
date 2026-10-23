"""Visual system for FinBridge Insights.

Palette drawn from Rwanda's terraced farmland:
  TEA     formal finance (bank, SACCO, MFI)
  SORGHUM informal finance (tontine, relatives)
  SOIL    the gap we are measuring
"""
import plotly.graph_objects as go
import streamlit as st

INK = "#1C2B24"
SLATE = "#56665E"
MIST = "#EEF2EC"
PAPER = "#FFFFFF"
LINE = "#C9D3CC"
TEA = "#2F6B4F"
SORGHUM = "#C2922A"
SOIL = "#8E3B2E"
FONT = "Atkinson Hyperlegible, 'Segoe UI', system-ui, sans-serif"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap');
html, body, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp [data-testid="stMarkdownContainer"], [data-testid="stSidebarNav"] a {{
  font-family: {FONT} !important;
}}
h1 {{ font-size: 2.1rem; line-height: 1.15; letter-spacing: -0.01em; color: {INK}; max-width: 30ch; }}
h2 {{ font-size: 1.4rem; color: {INK}; margin-top: 1.6rem; }}
h3 {{ font-size: 1.1rem; color: {INK}; }}
.block-container {{ max-width: 1100px; padding-top: 2rem; }}
.lede {{ font-size: 1.15rem; line-height: 1.55; color: {SLATE}; max-width: 68ch; }}
.fact {{ border-left: 4px solid {TEA}; padding: .2rem 0 .2rem .9rem; margin-bottom: 1rem; }}
.fact.gap {{ border-left-color: {SOIL}; }}
.fact.informal {{ border-left-color: {SORGHUM}; }}
.fact b {{ font-size: 1.9rem; color: {INK}; display: block; line-height: 1.1; }}
.fact span {{ color: {SLATE}; font-size: .95rem; }}
.note {{ color: {SLATE}; font-size: .9rem; max-width: 75ch; }}
a:focus-visible, button:focus-visible {{ outline: 3px solid {SORGHUM}; outline-offset: 2px; }}
</style>
"""


def apply():
    st.markdown(CSS, unsafe_allow_html=True)


def fact(value: str, text: str, kind: str = ""):
    st.markdown(f'<div class="fact {kind}"><b>{value}</b><span>{text}</span></div>',
                unsafe_allow_html=True)


def note(text: str):
    st.markdown(f'<p class="note">{text}</p>', unsafe_allow_html=True)


def layout(fig: go.Figure, height=360, showlegend=False, **kw) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=10, r=20, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=INK, size=14), showlegend=showlegend, **kw)
    fig.update_xaxes(gridcolor=LINE, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    return fig


def ci_bars(df, label_col="group", color=TEA, height=None, xmax=None, ticksuffix="%"):
    """Horizontal bars with 95% CI whiskers. Suppressed rows are labelled, not drawn."""
    d = df.copy()
    shown = d[d.est.notna()]
    colors = [SORGHUM if r == "caution" else color for r in shown.reliability]
    fig = go.Figure(go.Bar(
        y=shown[label_col], x=shown.est, orientation="h", marker_color=colors,
        error_x=dict(type="data", symmetric=False, array=shown.hi - shown.est,
                     arrayminus=shown.est - shown.lo, color=INK, thickness=1.2, width=4),
        customdata=shown[["lo", "hi", "n"]].values,
        hovertemplate="%{y}: %{x:.1f}%<br>95% CI %{customdata[0]:.1f}–%{customdata[1]:.1f}"
                      "<br>n = %{customdata[2]}<extra></extra>"))
    # value labels sit just past the upper confidence limit so they never collide with whiskers
    fig.add_trace(go.Scatter(
        y=shown[label_col], x=shown.hi, mode="text", text=[f"  {v:.1f}%" for v in shown.est],
        textposition="middle right", textfont=dict(color=INK, size=13), hoverinfo="skip"))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(ticksuffix=ticksuffix, range=[0, xmax or max(5, (shown.hi.max() or 0) * 1.25)])
    return layout(fig, height=height or 70 + 42 * len(shown))


def summary(key: str, **kw):
    """Kinyarwanda summary above a page whose body is still in English."""
    from src.i18n import t, lang
    if lang() == "rw":
        st.info(t(key, **kw) + "  \n" + t("lang.en_note"))
