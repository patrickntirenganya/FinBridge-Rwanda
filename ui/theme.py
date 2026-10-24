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

CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap');
:root{--ink:@INK;--slate:@SLATE;--mist:@MIST;--line:@LINE;--tea:@TEA;--tea-d:#1F4D38;--ochre:@SORGHUM;--soil:@SOIL;
 --card:#FFFFFF;--shadow:0 6px 24px rgba(31,77,56,.08);--shadow-h:0 12px 32px rgba(31,77,56,.16);--r:16px}
html,body,.stApp p,.stApp li,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp button,
.stApp [data-testid="stMarkdownContainer"],[data-testid="stSidebarNav"] a{font-family:@FONT !important}
.stApp{background:linear-gradient(180deg,#F5F8F4 0%,#EAF0EA 100%)}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1100px;padding-top:1.4rem;padding-bottom:4rem}
h1{font-size:2.1rem;line-height:1.15;letter-spacing:-.01em;color:var(--ink);max-width:30ch}
h2{font-size:1.45rem;color:var(--ink);margin-top:1.8rem;position:relative}
h3{font-size:1.1rem;color:var(--ink)}
h2::after{content:"";display:block;width:44px;height:4px;border-radius:4px;margin-top:.35rem;
 background:linear-gradient(90deg,var(--tea),var(--ochre));animation:grow .9s ease-out both}
.lede{font-size:1.15rem;line-height:1.55;color:var(--slate);max-width:68ch}
.note{color:var(--slate);font-size:.9rem;max-width:75ch}

/* ---------- animations ---------- */
@property --n{syntax:'<integer>';initial-value:0;inherits:false}
@property --t{syntax:'<integer>';initial-value:0;inherits:false}
@keyframes countup{from{--n:0;--t:0}}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes grow{from{width:0}to{width:44px}}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes glow{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-30px,18px) scale(1.12)}}
@keyframes shine{from{background-position:-200% 0}to{background-position:200% 0}}
.count{--n:var(--i);--t:var(--d);counter-reset:n var(--n) t var(--t);animation:countup 1.6s cubic-bezier(.2,.7,.2,1) both}
.count.dec::after{content:counter(n) "." counter(t)}
.count.int::after{content:counter(n)}

/* ---------- hero ---------- */
.hero{position:relative;overflow:hidden;border-radius:24px;padding:2.2rem 2.4rem 2.4rem;margin:.2rem 0 1.6rem;color:#F2F7F3;
 background:linear-gradient(135deg,#173A2B 0%,#1F4D38 45%,#2F6B4F 100%);box-shadow:0 18px 44px rgba(23,58,43,.28);animation:fadeUp .7s ease both}
.hero::before{content:"";position:absolute;right:-120px;top:-140px;width:420px;height:420px;border-radius:50%;
 background:radial-gradient(circle,rgba(194,146,42,.55),rgba(194,146,42,0) 65%);animation:glow 9s ease-in-out infinite}
.hero .hills{position:absolute;left:0;bottom:0;width:200%;height:90px;opacity:.5;animation:drift 38s linear infinite;
 background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 90' preserveAspectRatio='none'><path d='M0 60 Q75 25 150 55 T300 50 T450 58 T600 60 V90 H0Z' fill='%234A8B67' fill-opacity='.55'/><path d='M0 75 Q100 45 200 72 T400 70 T600 75 V90 H0Z' fill='%23173A2B' fill-opacity='.65'/></svg>") repeat-x;background-size:50% 100%}
.hero>*{position:relative}
.hero .pill{display:inline-block;font-size:.78rem;letter-spacing:.02em;padding:.3rem .8rem;border-radius:999px;
 background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.28);margin-bottom:.9rem}
.hero h1{color:#fff;font-size:2.5rem;max-width:22ch;margin:0 0 .6rem}
.hero p.lede{color:#DCEBE2;max-width:60ch;margin:0 0 1.3rem}
.chips{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:.4rem}
.chip{border-radius:16px;padding:1rem 1.1rem 1.05rem;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.24);
 backdrop-filter:blur(6px);animation:fadeUp .7s ease both;transition:transform .25s,background .25s}
.chip:nth-child(1){animation-delay:.15s}.chip:nth-child(2){animation-delay:.3s}.chip:nth-child(3){animation-delay:.45s}
.chip:hover{transform:translateY(-4px);background:rgba(255,255,255,.2)}
.chip b{display:block;font-size:2.3rem;line-height:1.05;color:#fff}
.chip>span{font-size:.92rem;color:#DCEBE2;line-height:1.35;display:block;margin-top:.25rem}
.chip.gap b{color:#FFD58A}

.hero .photo{position:absolute;right:0;top:0;bottom:0;width:42%;height:100%;object-fit:cover;opacity:.9;
 -webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 55%);mask-image:linear-gradient(90deg,transparent 0%,#000 55%)}
.hero.has-photo>h1,.hero.has-photo>.lede,.hero.has-photo>.pill{max-width:min(60ch,56%)}
.hero.has-photo .chips{max-width:min(100%,640px)}
.hero.compact{padding:1.5rem 2.4rem;min-height:130px;display:flex;align-items:center}.hero.compact h1{font-size:2rem;margin:0}
@media (max-width:700px){.hero .photo{display:none}.hero.has-photo>h1,.hero.has-photo>.lede,.hero.has-photo>.pill{max-width:none}}

/* ---------- cards and facts ---------- */
.fact{background:var(--card);border-radius:14px;border-left:5px solid var(--tea);padding:.85rem 1rem;margin-bottom:1rem;
 box-shadow:var(--shadow);transition:transform .25s,box-shadow .25s;animation:fadeUp .6s ease both}
.fact:hover{transform:translateY(-3px);box-shadow:var(--shadow-h)}
.fact.gap{border-left-color:var(--soil)}.fact.informal{border-left-color:var(--ochre)}
.fact b{font-size:1.6rem;color:var(--ink);display:block;line-height:1.1}
.fact>span{color:var(--slate);font-size:.95rem}
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]){border-radius:var(--r)}
div[data-testid="stVerticalBlockBorderWrapper"]{background:var(--card);border:1px solid #DDE6DF !important;border-radius:var(--r);
 box-shadow:var(--shadow);transition:transform .25s,box-shadow .25s}
div[data-testid="stVerticalBlockBorderWrapper"]:hover{box-shadow:var(--shadow-h);transform:translateY(-2px)}
[data-testid="stPlotlyChart"]{background:var(--card);border-radius:var(--r);box-shadow:var(--shadow);padding:.6rem .4rem 0;overflow:hidden}
[data-testid="stAlert"]{border-radius:14px;border:none;box-shadow:var(--shadow)}
[data-testid="stExpander"]{border-radius:14px;background:var(--card);border:1px solid #DDE6DF}
[data-testid="stDataFrame"]{border-radius:14px;overflow:hidden;box-shadow:var(--shadow)}

/* ---------- controls ---------- */
.stButton>button,.stDownloadButton>button,[data-testid="stBaseButton-secondaryFormSubmit"],[data-testid="stBaseButton-primaryFormSubmit"]{
 border-radius:12px;font-weight:700;border:1.5px solid #CBD8CF;transition:transform .2s,box-shadow .2s,background .2s}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(31,77,56,.18);border-color:var(--tea)}
button[kind="primary"],button[data-testid="stBaseButton-primary"],button[data-testid="stBaseButton-primaryFormSubmit"]{
 background:linear-gradient(135deg,#2F6B4F,#1F4D38) !important;color:#fff !important;border:none !important;box-shadow:0 6px 16px rgba(31,77,56,.28)}
button[kind="primary"]:hover,button[data-testid="stBaseButton-primary"]:hover{background:linear-gradient(135deg,#3A7F5E,#2F6B4F) !important}
button:active{transform:scale(.98) !important}
[role="tablist"]{gap:.4rem;background:#E3EBE5;padding:.3rem;border-radius:14px;border:none;box-shadow:none}
[data-testid="stTab"],button[role="tab"]{border-radius:11px;padding:.5rem 1.1rem;color:var(--slate);font-weight:700;cursor:pointer;transition:background .2s,color .2s,box-shadow .2s}
[data-testid="stTab"]:hover,button[role="tab"]:hover{background:rgba(255,255,255,.65)}
[data-testid="stTab"][aria-selected="true"],button[role="tab"][aria-selected="true"]{background:#fff !important;color:var(--tea) !important;box-shadow:0 2px 8px rgba(31,77,56,.14)}
[data-testid="stTab"][aria-selected="true"] p{color:var(--tea)}
.react-aria-SelectionIndicator,[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none !important}
input,textarea,[data-baseweb="select"]>div{border-radius:11px !important}
a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--ochre);outline-offset:2px}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#173A2B 0%,#1F4D38 100%)}
[data-testid="stSidebar"] *{color:#E8F0EA}
[data-testid="stSidebar"] [data-testid="stLogo"]{height:2.4rem}
[data-testid="stSidebarNav"] a{border-radius:11px;transition:background .2s,transform .2s;padding:.38rem .6rem}
[data-testid="stSidebarNav"] a:hover{background:rgba(255,255,255,.1);transform:translateX(3px)}
[data-testid="stSidebarNav"] a[aria-current="page"]{background:rgba(255,255,255,.18);box-shadow:inset 3px 0 0 var(--ochre)}
[data-testid="stSidebarNav"] span[data-testid="stNavSectionHeader"],[data-testid="stSidebarNavSeparator"]{opacity:.75}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.18)}
[data-testid="stSidebar"] [data-baseweb="radio"] div{color:#E8F0EA}

/* ---------- small screens and reduced motion ---------- */
@media (max-width:700px){
 .block-container{padding-left:1rem;padding-right:1rem}
 h1{font-size:1.65rem}.hero{padding:1.4rem 1.2rem 1.7rem;border-radius:18px}
 .hero h1{font-size:1.75rem}.chips{grid-template-columns:1fr}.chip b{font-size:1.9rem}
 .stTabs [data-baseweb="tab"]{padding:.45rem .7rem}}
@media (prefers-reduced-motion:reduce){
 *,*::before,*::after{animation:none !important;transition:none !important}}
</style>
"""
CSS = (CSS_TEMPLATE.replace("@INK", INK).replace("@SLATE", SLATE).replace("@MIST", MIST).replace("@LINE", LINE)
       .replace("@TEA", TEA).replace("@SORGHUM", SORGHUM).replace("@SOIL", SOIL).replace("@FONT", FONT))


def apply():
    st.markdown(CSS, unsafe_allow_html=True)


def count_html(text: str) -> str:
    """Animate a short figure like '62.7%', '≈759k' or '14%'. Longer or formatted numbers stay static."""
    import re
    m = re.fullmatch(r"(≈?)(\d{1,3})(?:\.(\d))?(%|k)?", text.strip())
    if not m:
        return text
    pre, whole, dec, suf = m.group(1), m.group(2), m.group(3), m.group(4) or ""
    cls = "dec" if dec is not None else "int"
    return (f'{pre}<span class="count {cls}" style="--i:{whole};--d:{dec or 0}" aria-label="{text}"></span>{suf}')


def fact(value: str, text: str, kind: str = ""):
    st.markdown(f'<div class="fact {kind}"><b>{count_html(value)}</b><span>{text}</span></div>',
                unsafe_allow_html=True)


@st.cache_data
def _photo(name: str) -> str:
    """Photo from ui/assets/photos as a data URI, so the banner needs no static file hosting."""
    import base64
    from pathlib import Path
    raw = (Path(__file__).parent / "assets" / "photos" / f"{name}.webp").read_bytes()
    return "data:image/webp;base64," + base64.b64encode(raw).decode()


def hero(title: str, lede: str = "", pill: str = "", chips: list[tuple[str, str, str]] | None = None,
         photo: str = ""):
    """Banner with drifting terraces and count-up figures. chips = [(value, label, kind), ...].
    photo = a name in ui/assets/photos (decorative, so alt text is empty)."""
    cs = "".join(f'<div class="chip {k}"><b>{count_html(v)}</b><span>{lab}</span></div>' for v, lab, k in (chips or []))
    cls = "hero" + (" has-photo" if photo else "") + ("" if lede or chips else " compact")
    html = (f'<div class="{cls}">' + (f'<img class="photo" src="{_photo(photo)}" alt="">' if photo else "")
            + '<div class="hills"></div>'
            + (f'<div class="pill">{pill}</div>' if pill else "")
            + f'<h1>{title}</h1>' + (f'<p class="lede">{lede}</p>' if lede else "")
            + (f'<div class="chips">{cs}</div>' if cs else "") + "</div>")
    st.markdown(html, unsafe_allow_html=True)


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
