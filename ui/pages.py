"""Page functions for FinBridge Insights. Each reads only aggregate tables."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.i18n import t
from ui import theme as T
from ui.data import load, ordered

D = load()

AHS_SRC = "Source: NISR Agricultural Household Survey 2024 (RWA-NISR-RAHS-2024-V0.1), agricultural households, weighted."
FS_SRC = ("Source: NISR/AFR FinScope Rwanda 2024 (RWA-NISR-FINSCOPE-2024-v01), adults 16+, weighted. "
          "The public file has no cluster variable, so intervals are narrower than the true uncertainty.")

PROVINCE_OF = {  # district -> province (NISR district codes: first digit = province)
    **dict.fromkeys(["Nyarugenge", "Gasabo", "Kicukiro"], "Kigali"),
    **dict.fromkeys(["Nyanza", "Gisagara", "Nyaruguru", "Huye", "Nyamagabe", "Ruhango", "Muhanga", "Kamonyi"], "South"),
    **dict.fromkeys(["Karongi", "Rutsiro", "Rubavu", "Nyabihu", "Ngororero", "Rusizi", "Nyamasheke"], "West"),
    **dict.fromkeys(["Rulindo", "Gakenke", "Musanze", "Burera", "Gicumbi"], "North"),
    **dict.fromkeys(["Rwamagana", "Nyagatare", "Gatsibo", "Kayonza", "Kirehe", "Ngoma", "Bugesera"], "East"),
}



def pick(container, label, options, default=None):
    """Selectbox over human labels; returns the underlying key. options: pd.Series key -> label."""
    keys, labs = list(options.index), list(options.values)
    i = keys.index(default) if default in keys else 0
    chosen = container.selectbox(label, labs, index=i)
    return keys[labs.index(chosen)]


def nat(table, key):
    r = D[table].set_index("indicator").loc[key]
    return r


def compare_sentence(df):
    """Plain-language check of whether the highest and lowest groups really differ."""
    d = df[df.est.notna()]
    if len(d) < 2:
        return ""
    hi, lo = d.loc[d.est.idxmax()], d.loc[d.est.idxmin()]
    clear = hi.lo > lo.hi
    verdict = ("The intervals do not overlap, so this difference is statistically clear."
               if clear else "The intervals overlap, so the data cannot confirm a real difference.")
    return f"Highest: **{hi.group}** ({hi.est:.1f}%). Lowest: **{lo.group}** ({lo.est:.1f}%). {verdict}"


# ------------------------------------------------------------------ pages
def overview():
    seg = D["ahs_segments"].set_index("segment")
    gap = D["ahs_national"].set_index("indicator").loc["banked_not_financed"]
    T.hero(t("ov.title"), t("ov.lede", g=f"{gap.est:.1f}", lo=f"{gap.lo:.1f}", hi=f"{gap.hi:.1f}"), t("hero.pill"), photo="farmer-beans")

    parts = [("Account and formal loan", T.TEA), ("Account, borrowed only informally", T.SOIL),
             ("Account, did not borrow", "#8FB5A0"), ("No formal account", T.LINE)]
    fig = go.Figure()
    for name, col in parts:
        r = seg.loc[name]
        name = t(f"ov.seg.{name}")
        fig.add_bar(y=[t("ov.hh")], x=[r.est], name=name, orientation="h",
                    marker_color=col, text=f"{r.est:.0f}%", textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color="white" if col in (T.TEA, T.SOIL) else "#1C2B24" if col == "#8FB5A0" else T.INK, size=16),
                    hovertemplate=f"{name}: {r.est:.1f}% (95% CI {r.lo:.1f}–{r.hi:.1f})<extra></extra>")
    T.layout(fig, height=240, barmode="stack", showlegend=True,
             legend=dict(orientation="h", y=-0.6, x=0, font=dict(size=13), traceorder="normal"))
    fig.update_xaxes(range=[0, 100], ticksuffix="%", showgrid=False)
    fig.update_yaxes(showticklabels=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    hh = D["meta"]["ahs_weighted_households"]
    informal = seg.loc["Account, borrowed only informally"]
    c1, c2, c3 = st.columns(3)
    with c1:
        T.fact(f"{nat('ahs_national', 'acct_formal').est:.1f}%", t("ov.f1"))
    with c2:
        T.fact(f"{nat('ahs_national', 'loan_formal').est:.1f}%", t("ov.f2"), "gap")
    with c3:
        T.fact(f"≈{informal.est / 100 * hh / 1000:,.0f}k", t("ov.f3"), "informal")

    st.subheader(t("ov.sub"))
    src = D["ahs_loan_sources"].sort_values("est", ascending=False)
    fig = T.ci_bars(src.rename(columns={"category": "group"}), color=T.SORGHUM)
    fig.data[0].marker.color = [{"formal": T.TEA, "informal": T.SORGHUM}.get(k, "#9AA8A0") for k in src.kind]
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    T.note(t("ov.note") + " " + AHS_SRC)


def who():
    T.hero("Who gets formal credit", photo="farmer-beans")
    T.summary("sum.who")
    st.markdown('<p class="lede">Compare agricultural households by welfare, land, gender and '
                'cooperative membership. Bars show 95% confidence intervals; ochre bars are less '
                'precise (coefficient of variation above 30%).</p>', unsafe_allow_html=True)
    bg = D["ahs_by_group"]
    inds = bg.drop_duplicates("indicator").set_index("indicator").label
    groups = bg[bg.group_var != "district"].drop_duplicates("group_var").set_index("group_var").group_label
    c1, c2 = st.columns(2)
    ind = pick(c1, "Indicator", inds, "loan_formal")
    grp = pick(c2, "Compare by", groups)
    d = ordered(bg[(bg.indicator == ind) & (bg.group_var == grp)], grp)
    st.plotly_chart(T.ci_bars(d), use_container_width=True, config={"displayModeBar": False})
    st.markdown(compare_sentence(d))
    T.note("These are associations, not causes: richer households, for example, also tend to farm "
           "more land and hold titles. " + AHS_SRC)
    with st.expander("Show the numbers"):
        st.dataframe(d[["group", "est", "lo", "hi", "n", "reliability"]], hide_index=True)


def why():
    T.hero("What loans are for, and why they are refused", photo="farmer-weeding")
    pur = D["ahs_loan_purpose"].sort_values("est", ascending=False)
    _p = D["ahs_loan_purpose"].set_index("category")
    T.summary("sum.why", food=f"{_p.loc['Food purchase'].est:.1f}", inp=f"{_p.loc['Agricultural inputs'].formal_source_pct:.1f}")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Share of loans by purpose")
        st.plotly_chart(T.ci_bars(pur.rename(columns={"category": "group"}), color=T.SORGHUM),
                        use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.subheader("Share of those loans from a formal lender")
        fp = pur.dropna(subset=["formal_source_pct"])
        fig = go.Figure(go.Bar(y=fp.category, x=fp.formal_source_pct, orientation="h",
                               marker_color=[T.TEA if a else "#8FB5A0" for a in fp.agri_purpose],
                               text=[f"{v:.0f}%" for v in fp.formal_source_pct], textposition="outside"))
        fig.update_yaxes(autorange="reversed"); fig.update_xaxes(ticksuffix="%", range=[0, 35])
        st.plotly_chart(T.layout(fig, height=70 + 42 * len(fp)), use_container_width=True,
                        config={"displayModeBar": False})
    T.note("Food purchases are the most common reason to borrow. Loans for farm inputs, equipment "
           "and livestock (dark green) rarely come from formal lenders. " + AHS_SRC)

    st.subheader("Reasons given for loan refusals")
    den = D["ahs_denial_reasons"].sort_values("est", ascending=False)
    st.plotly_chart(T.ci_bars(den.rename(columns={"category": "group"}), color=T.SOIL),
                    use_container_width=True, config={"displayModeBar": False})
    T.note(f"Based on {int(den.n.iloc[0])} refusals only, so intervals are wide. Treat as indicative. "
           + AHS_SRC)

    st.subheader("Why adults do not borrow or bank (FinScope)")
    b = D["fs_barriers"]
    qs = b.drop_duplicates("question").set_index("question").question_label
    c1, c2 = st.columns(2)
    q = pick(c1, "Question", qs)
    seg = c2.selectbox("Group", ["All adults", "Farming only", "Farming + other work", "Not farming"])
    d = b[(b.question == q) & (b.segment == seg)].sort_values("est", ascending=False).head(8)
    st.plotly_chart(T.ci_bars(d.rename(columns={"category": "group"}), color=T.SOIL),
                    use_container_width=True, config={"displayModeBar": False})
    T.note(FS_SRC)


def farmers():
    T.hero("Farmers compared with other adults", photo="farmer-phone-call")
    T.summary("sum.farmers")
    st.markdown('<p class="lede">FinScope covers all adults, so it shows how people in farming '
                'households compare with everyone else.</p>', unsafe_allow_html=True)
    fb = D["fs_by_group"]
    inds = fb.drop_duplicates("indicator").set_index("indicator").label
    groups = fb[fb.group_var != "district"].drop_duplicates("group_var").set_index("group_var").group_label
    c1, c2 = st.columns(2)
    ind = pick(c1, "Indicator", inds, "formal_credit")
    grp = pick(c2, "Compare by", groups)
    d = ordered(fb[(fb.indicator == ind) & (fb.group_var == grp)], grp)
    st.plotly_chart(T.ci_bars(d), use_container_width=True, config={"displayModeBar": False})
    st.markdown(compare_sentence(d))
    T.note("Our formal saving, credit and insurance definitions are narrower than FinScope's official "
           "strands (see Methods), so use these for comparing groups rather than as national totals. " + FS_SRC)


def opportunity():
    T.hero(t("opp.title"), photo="farmer-field")
    T.summary("sum.opportunity", pct=f"{D['ahs_segments'].set_index('segment').est['Account, borrowed only informally']:.1f}")
    d = D["ahs_district_opportunity"].copy()
    ok = d[d.reliability != "suppressed"]
    seg = D["ahs_segments"].set_index("segment").loc["Account, borrowed only informally"]
    national = seg.est / 100 * D["meta"]["ahs_weighted_households"]
    st.markdown(
        '<p class="lede">These are households that already save with a bank, SACCO or microfinance institution '
        "but borrowed only informally, for example from a tontine. Nationally that is "
        f"<b>{seg.est:.1f}%</b> of agricultural households, about <b>{national / 1000:,.0f}k</b>. "
        "The map shows where they live. It does not say they want or qualify for a loan.</p>", unsafe_allow_html=True)
    mode = st.radio("Show", ["Number of households", "Share of district households"], horizontal=True,
                    key="opp_mode")
    counts = mode.startswith("Number")
    c1, c2 = st.columns([4, 6])
    with c1:
        st.plotly_chart(_opportunity_map(d, counts), use_container_width=True, config={"displayModeBar": False})
    with c2:
        def cell(r):
            if pd.isna(r.households):
                return "not reported (too few sampled)"
            return f"{r.households:,.0f} ({r.hh_lo:,.0f}–{r.hh_hi:,.0f})" + ("  ⚠ caution" if r.reliability == "caution" else "")
        tab = d.sort_values("households", ascending=False, na_position="last")
        tab = pd.DataFrame({"District": tab.district, "Households (95% range)": [cell(r) for r in tab.itertuples()],
                            "Share (95% CI)": [("" if pd.isna(r.pct) else f"{r.pct:.1f}% ({r.lo:.1f}–{r.hi:.1f})") for r in tab.itertuples()]})
        st.dataframe(tab, hide_index=True, height=520, use_container_width=True,
                     column_config={"District": st.column_config.TextColumn(width="small")})
    st.caption(f"The {len(ok)} districts with enough sampled households add up to {ok.households.sum() / 1000:,.0f}k of "
               f"the national ≈{national / 1000:,.0f}k. The remainder is in the {len(d) - len(ok)} Kigali districts "
               "shown in grey (fewer than 30 sampled households each), so their counts are not reported. Sampled households per "
               "district range from "
               f"{int(d.n.min())} to {int(d.n.max())}; hover over a district on the map to see its own n.")
    shaky = d[d.reliability == "caution"]
    if len(shaky):
        st.warning("Estimates for " + ", ".join(shaky.district) + " are imprecise (coefficient of variation above 0.30). "
                   "Do not rank them against other districts.")
    _tontine_bridge()
    T.note("Districts are sorted by estimated count, not ranked: intervals overlap, so neighbouring districts often do "
           "not differ clearly. Counts = district share x weighted households in the district. "
           + AHS_SRC + " Boundaries: geoBoundaries (CC BY 4.0), simplified; for display only.")


def _tontine_bridge():
    """F2: savings groups that already connect to SACCOs, as in India's SHG-Bank Linkage."""
    b = D["ahs_tontine_bridge"].set_index("indicator")
    st.subheader(t("ton.title"))
    st.markdown(t("ton.lede"))
    steps = [("tontine_member", "ton.s1", ""), ("acct_sacco", "ton.s2", "informal"), ("farm_loan", "ton.s3", "")]
    for col, (key, base_key, kind) in zip(st.columns(3), steps):
        r = b.loc[key]
        with col:
            T.fact(f"{r.est:.1f}%", t(base_key), kind)
            st.caption(f"95% CI {r.lo:.1f}–{r.hi:.1f} · n = {int(r.n):,} · {r.base}")
    st.info(t("ton.india"))
    T.note(AHS_SRC + " " + t("ton.note"))


def _opportunity_map(d, counts):
    from ui.data import districts_geojson
    geo = districts_geojson()
    ok = d[d.reliability != "suppressed"]
    grey = d[d.reliability == "suppressed"]
    z, unit = (ok.households, "households") if counts else (ok.pct, "%")
    fig = go.Figure(go.Choroplethmap(
        geojson=geo, featureidkey="properties.shapeName", locations=ok.district, z=z, zmin=0,
        colorscale=[[0, T.LOW], [1, T.TEA]], marker_line_color=T.CARD, marker_line_width=0.8, marker_opacity=0.95,
        colorbar=dict(title="" if counts else "%", thickness=12, len=0.6, ticksuffix="" if counts else "%",
                      x=0.95, xanchor="left"),
        customdata=ok[["hh_lo", "hh_hi", "pct", "lo", "hi", "n"]].values,
        hovertemplate="%{location}<br>" + ("%{z:,.0f} households (95% %{customdata[0]:,.0f}–%{customdata[1]:,.0f})"
                                           if counts else "%{z:.1f}% (95% CI %{customdata[3]:.1f}–%{customdata[4]:.1f})")
                      + "<br>sampled n = %{customdata[5]}<extra></extra>"))
    if len(grey):
        fig.add_trace(go.Choroplethmap(
            geojson=geo, featureidkey="properties.shapeName", locations=grey.district, z=[0] * len(grey),
            colorscale=[[0, "#B9C3BC"], [1, "#B9C3BC"]], showscale=False, marker_line_color=T.CARD,
            marker_line_width=0.8, marker_opacity=0.95, customdata=grey[["n"]].values,
            hovertemplate="%{location}<br>Too few sampled households<br>n = %{customdata[0]}<extra></extra>"))
    fig.update_layout(map=dict(style=T.map_style(), center=dict(lat=-1.95, lon=29.88), zoom=6.75), height=520,
                      margin=dict(l=0, r=44, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=T.FONT, color=T.INK, size=13))
    return fig


def _paired(df, inds, names, colors, groups):
    """Grouped bars with 95% CI whiskers: one cluster per indicator, one bar per group. Labels sit above the whisker."""
    fig = go.Figure()
    for g, col in zip(groups, colors):
        r = df[df.group == g].set_index("indicator").reindex(inds)
        fig.add_bar(name=g, x=[names[i] for i in inds], y=r.est, marker_color=col, offsetgroup=g,
                    error_y=dict(type="data", symmetric=False, array=r.hi - r.est, arrayminus=r.est - r.lo,
                                 color=T.INK, thickness=1.2, width=4),
                    customdata=r[["lo", "hi", "n"]].values,
                    hovertemplate="%{x}<br>" + g + ": %{y:.1f}% (95% CI %{customdata[0]:.1f}–%{customdata[1]:.1f})"
                                  "<br>n = %{customdata[2]}<extra></extra>")
        fig.add_trace(go.Scatter(x=[names[i] for i in inds], y=r.hi, mode="text", text=[f"{v:.1f}%" for v in r.est],
                                 textposition="top center", textfont=dict(size=10, color=T.INK), showlegend=False,
                                 hoverinfo="skip", offsetgroup=g, cliponaxis=False))
    top = max(df[df.group.isin(groups) & df.indicator.isin(inds)].hi.max() * 1.15, 5)
    fig.update_yaxes(ticksuffix="%", range=[0, top], gridcolor=T.LINE)
    fig.update_xaxes(gridcolor="rgba(0,0,0,0)")
    return T.layout(fig, height=420, showlegend=True, barmode="group", legend=dict(orientation="h", y=1.12))


def social():
    T.hero(t("soc.title"), photo="farmer-phone-call")
    T.summary("sum.social")
    fs = D["fs_by_group"]
    vup = fs[fs.group_var == "vup"]
    ub = fs[fs.group_var == "ubudehe_1"]
    g = lambda tab, ind, grp: tab[(tab.indicator == ind) & (tab.group == grp)].iloc[0]
    V, N = "Received VUP cash transfer", "Did not receive one"
    st.markdown(
        '<p class="lede">The Vision Umurenge Programme (VUP) pays direct cash transfers to the poorest households. '
        "Are those households also connected to formal finance? Among adults in households that received a transfer, "
        f"<b>{g(vup, 'bank_acct', V).est:.1f}%</b> have a bank account, against <b>{g(vup, 'bank_acct', N).est:.1f}%</b> "
        "elsewhere. These are associations, not effects of the programme.</p>", unsafe_allow_html=True)
    names = {"bank_acct": "Bank account", "momo_registered": "Mobile money", "formal_saving": "Formal saving",
             "emergency_fund": "Emergency fund", "insured": "Insurance"}
    inds = list(names)
    st.subheader("1. Households that received a VUP cash transfer")
    st.plotly_chart(_paired(vup, inds, names, [T.SOIL, T.TEA], [V, N]), use_container_width=True,
                    config={"displayModeBar": False})
    T.note(f"{int(g(vup, 'bank_acct', V).n):,} sampled adults in transfer households vs "
           f"{int(g(vup, 'bank_acct', N).n):,} others. Households answering 'don't know' are left out. {FS_SRC}")

    st.subheader("2. Formal credit looks similar, but part of it is a government loan")
    cn = {"formal_credit": "Formal credit (as defined here)", "formal_credit_ex_govt": "Excluding Ubudehe/VUP loans",
          "govt_loan": "Ubudehe / VUP loan only"}
    st.plotly_chart(_paired(vup, list(cn), cn, [T.SOIL, T.TEA], [V, N]), use_container_width=True,
                    config={"displayModeBar": False})
    st.markdown(
        "Our formal-credit definition counts a loan from the Government Ubudehe credit scheme or VUP as formal. "
        f"Without it, the transfer group's rate is **{g(vup, 'formal_credit_ex_govt', V).est:.1f}%** against "
        f"**{g(vup, 'formal_credit_ex_govt', N).est:.1f}%** for others. Shown separately so the comparison is transparent.")

    st.subheader("3. Ubudehe category 1 (the poorest) compared with other categories")
    U1, UO = "Ubudehe category 1", "Other categories"
    st.plotly_chart(_paired(ub, inds + ["formal_credit"], {**names, "formal_credit": "Formal credit"},
                            [T.SOIL, T.TEA], [U1, UO]), use_container_width=True, config={"displayModeBar": False})

    st.subheader("4. Farm households: formal loans by poverty status")
    ahs = D["ahs_by_group"]
    pov = ahs[(ahs.indicator == "loan_formal") & (ahs.group_var == "poverty")]
    st.plotly_chart(T.ci_bars(pov.assign(group=pov.group.map({"Poor": "Poor households", "Not poor": "Not poor"}))),
                    use_container_width=True, config={"displayModeBar": False})
    vs = D["ahs_loan_sources"].set_index("code").loc[7]
    st.markdown(f"VUP financial services are the source of **{vs.est:.1f}%** of all loans reported by agricultural "
                f"households (95% CI {vs.lo:.1f}–{vs.hi:.1f}).")
    T.note(AHS_SRC + " Poverty status from EICV7.")

    st.subheader("A route to consider: graduation")
    st.info("The graduation approach pairs a transfer of assets and support with coaching and savings. Randomised trials in "
            "six countries found lasting gains in consumption and assets (Banerjee et al., *Science*, 2015: "
            "[paper](https://economics.mit.edu/sites/default/files/2022-08/science.1260799.pdf)). Connecting transfer "
            "recipients to a SACCO account is a hypothesis for Rwanda, not something these data show. FinScope intervals "
            "are understated because the public file has no cluster variable.")


def districts():
    T.hero("District patterns", photo="farmer-field")
    T.summary("sum.districts")
    st.markdown('<p class="lede">Districts are listed by province, not ranked. Each district has '
                'roughly 120 sampled agricultural households, so intervals are wide and small '
                'differences are not meaningful.</p>', unsafe_allow_html=True)
    src = st.radio("Survey", ["Agricultural households (AHS)", "All adults (FinScope)"], horizontal=True)
    tab = D["ahs_by_group"] if src.startswith("Agri") else D["fs_by_group"]
    inds = tab.drop_duplicates("indicator").set_index("indicator").label
    default = "loan_formal" if src.startswith("Agri") else "formal_credit"
    ind = pick(st, "Indicator", inds, default)
    d = tab[(tab.indicator == ind) & (tab.group_var == "district")].copy()
    d["province"] = d.group.map(PROVINCE_OF)
    d = d.sort_values(["province", "group"])
    d["group"] = d.province + " · " + d.group
    nat_tab = D["ahs_national"] if src.startswith("Agri") else D["fs_national"]
    national = nat_tab.set_index("indicator").loc[ind].est
    cmap, cbars = st.columns([1, 1])
    with cmap:
        st.plotly_chart(_district_map(d, national), use_container_width=True, config={"displayModeBar": False})
    with cbars:
        fig = T.ci_bars(d, height=80 + 26 * len(d))
        fig.add_vline(x=national, line_dash="dot", line_color=T.SOIL,
                      annotation_text=f"National {national:.1f}%", annotation_position="top")
        fig.update_traces(textfont_size=11)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    shaky = d[d.reliability != "ok"]
    if len(shaky):
        names = ", ".join(sorted(g.split(" · ")[-1] for g in shaky.group))
        st.caption(f"Grey on the map: estimate unreliable or suppressed ({names}).")
    T.note((AHS_SRC if src.startswith("Agri") else FS_SRC) + " Suppressed cells (n < 30) are omitted. "
           "District boundaries: geoBoundaries (CC BY 4.0), simplified; for display only.")


def _district_map(d, national):
    """Choropleth of one indicator. Unreliable (CV > 0.30) or suppressed districts are grey."""
    from ui.data import districts_geojson
    geo = districts_geojson()
    d = d.assign(name=d.group.str.split(" · ").str[-1])
    ok = d[(d.reliability == "ok") & d.est.notna()]
    names = [f["properties"]["shapeName"] for f in geo["features"]]
    grey = [n for n in names if n not in set(ok.name)]
    hi = max(ok.est.max(), 1) if len(ok) else 1
    fig = go.Figure()
    fig.add_trace(go.Choroplethmap(
        geojson=geo, featureidkey="properties.shapeName", locations=ok.name, z=ok.est, zmin=0, zmax=hi,
        colorscale=[[0, T.LOW], [1, T.TEA]], marker_line_color=T.CARD, marker_line_width=0.8,
        marker_opacity=0.95, colorbar=dict(title="%", thickness=12, len=0.6, ticksuffix="%", x=0.95, xanchor="left"),
        customdata=ok[["lo", "hi", "n"]].values,
        hovertemplate="%{location}: %{z:.1f}%<br>95% CI %{customdata[0]:.1f}–%{customdata[1]:.1f}"
                      "<br>n = %{customdata[2]}<extra></extra>"))
    if grey:
        gd = d.set_index("name").reindex(grey)
        fig.add_trace(go.Choroplethmap(
            geojson=geo, featureidkey="properties.shapeName", locations=grey, z=[0] * len(grey),
            colorscale=[[0, "#B9C3BC"], [1, "#B9C3BC"]], showscale=False, marker_line_color=T.CARD,
            marker_line_width=0.8, marker_opacity=0.95, customdata=gd[["n"]].fillna(0).values,
            hovertemplate="%{location}<br>Estimate unreliable or suppressed<br>n = %{customdata[0]:.0f}<extra></extra>"))
    fig.update_layout(map=dict(style=T.map_style(), center=dict(lat=-1.95, lon=29.88), zoom=6.75),
                      height=520, margin=dict(l=0, r=44, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=T.FONT, color=T.INK, size=13))
    return fig


def methods():
    T.hero("Data and methods", photo="farmer-weeding")
    T.summary("sum.methods")
    m = D["meta"]
    st.markdown(f"""
**Datasets.** NISR Agricultural Household Survey 2024 ({m['ahs_households']:,} households in
{m['ahs_psu']} clusters, weighted to {m['ahs_weighted_households']:,} agricultural households) and
FinScope Rwanda 2024 ({m['finscope_adults']:,} adults, weighted to {m['finscope_weighted_adults']:,}).
Both are public-use files from the [NISR Microdata Portal](https://microdata.statistics.gov.rw/index.php/catalog).
The surveys cover different samples and are never linked record by record; they are shown side by side.

**Estimation.** All figures are survey-weighted. AHS intervals use Taylor linearisation with clusters as
primary sampling units and districts as strata. The public FinScope file has no cluster variable, so its
intervals treat each respondent independently and understate uncertainty. Cells with fewer than
{m['min_n']} respondents are suppressed.

**What this tool is not.** It does not score individuals, predict loan default or make lending decisions.
It describes patterns across groups of households.
""")
    st.markdown("""
**District map.** Boundaries from [geoBoundaries](https://www.geoboundaries.org) (source: Open Data Rwanda / NISR,
2012 boundaries), licence CC BY 4.0, simplified for display. Runfola et al. (2020), *PLoS ONE* 15(4): e0231866.

**Opportunity counts.** Households with a bank, SACCO or MFI account that borrowed only informally, per district:
the weighted district share (design-based CI) multiplied by the district's weighted household count. Districts with
fewer than 30 sampled households are not reported, so the 27 reported districts sum to slightly less than the national
total.
""")
    st.subheader("Checks against published figures")
    st.dataframe(D["validation"], hide_index=True, use_container_width=True)
    T.note("AHS figures reproduce NISR's published tables. For FinScope, mobile money and bank accounts match; "
           "the official saving, credit and insurance strands use definitions whose code is not public, "
           "so our transparent definitions are lower and are used for group comparisons only.")
    st.caption(f"Aggregates built {m['built']}.")


# ------------------------------------------------------------ recommendations
def _grp(var, indicator="loan_formal"):
    bg = D["ahs_by_group"]
    return bg[(bg.indicator == indicator) & (bg.group_var == var)].set_index("group")


def _clear(a, b):
    """True when the two confidence intervals do not overlap."""
    return a.lo > b.hi or b.lo > a.hi


LINKS: dict = {}   # evidence page key -> st.Page, set by app.py so cards can link to the pages their figures come from

SRC_PBC = "https://camlmac.pbc.gov.cn/en/3688110/3688172/4048362/2025080817551068801/index.html"
SRC_NABARD = "https://findevgateway.org/sites/default/files/publications/files/mfg-en-paper-nabard-and-microfinance-2002.pdf"
SRC_OAF = "https://www.globalgiving.org/pfil/59148/2025_Q4_One_Acre_Fund_Performance_Report.pdf"
SRC_GRAD = "https://economics.mit.edu/sites/default/files/2022-08/science.1260799.pdf"


def recommendation_cards():
    """Five cards that follow doc 02 section 4, then two further ideas the data allow. Pure data (tested)."""
    seg = D["ahs_segments"].set_index("segment")
    nat_ = D["ahs_national"].set_index("indicator")
    hh = D["meta"]["ahs_weighted_households"]
    purpose = D["ahs_loan_purpose"].set_index("category")
    br = D["ahs_tontine_bridge"].set_index("indicator")
    informal = seg.loc["Account, borrowed only informally"]
    sex, size, title, coop = _grp("head_sex"), _grp("farm_size"), _grp("titled"), _grp("coop_member")
    f, m = sex.loc["Female-headed"], sex.loc["Male-headed"]
    small, large = size.loc["< 0.1 ha"], size.loc["> 1 ha"]
    tit, notit = title.loc["Has titled land"], title.loc["No titled land"]
    cm, nm = coop.loc["Cooperative member"], coop.loc["Not a member"]
    inputs, acct_sex = purpose.loc["Agricultural inputs"], _grp("head_sex", "acct_formal")
    fs = D["fs_by_group"]
    vup = fs[(fs.group_var == "vup") & (fs.indicator == "bank_acct")].set_index("group")
    vy, vn = vup.loc["Received VUP cash transfer"], vup.loc["Did not receive one"]
    clear = lambda a, b_: "Evidence-backed" if _clear(a, b_) else "Hypothesis"
    return [
        dict(n=1, title="SACCO credit for existing savers", finding="Evidence-backed", who="SACCOs, banks, microfinance institutions",
             data=f"{informal.est:.1f}% of agricultural households (about {informal.est / 100 * hh / 1000:,.0f}k) hold a bank, SACCO or "
                  f"microfinance account yet borrowed only informally. {nat_.loc['acct_sacco'].est:.1f}% have a SACCO account; "
                  f"{nat_.loc['loan_formal'].est:.1f}% have a formal loan.",
             hypothesis="That the savings history a SACCO already holds can predict repayment well enough to offer these savers "
                        "credit. This is untested here; a small pilot would test it.",
             model="China's credit-household files: rural credit cooperatives keep a credit record on each household and extend "
                   "small loans without collateral to rated households.", model_url=SRC_PBC, page="opportunity",
             page_label="Where SACCOs could reach savers"),
        dict(n=2, title="Link tontines to SACCOs", finding="Evidence-backed", who="SACCOs, cooperatives, MINAGRI",
             data=f"{br.loc['tontine_member'].est:.1f}% of agricultural households have a tontine member, and "
                  f"{br.loc['acct_sacco'].est:.1f}% of tontine borrowers already hold a SACCO account.",
             hypothesis="That group loans backed by group savings would reach members who do not borrow formally today. "
                        "The data show the overlap, not that it would lead to loans.",
             model="India's SHG-Bank Linkage: banks lend to savings groups in multiples of group savings, without collateral.",
             model_url=SRC_NABARD, page="opportunity", page_label="Tontines: an existing bridge"),
        dict(n=3, title="Season-shaped input credit", finding="Evidence-backed", who="Lenders, input suppliers, MINAGRI",
             data=f"About 1 in 9 loans ({inputs.est:.1f}%) is for farm inputs. Among those input loans, only "
                  f"{inputs.formal_source_pct:.1f}% came from a formal lender; the rest came from tontines, relatives and others. "
                  "(The first figure counts loans by purpose, the second counts them by lender.)",
             hypothesis="That input credit repaid flexibly across the season would raise uptake at SACCOs.",
             model="One Acre Fund (Tubura): seed and fertiliser on credit, repaid in any amount before the deadline; its "
                   "preliminary 2025 Rwanda repayment was 99%.", model_url=SRC_OAF, page="why",
             page_label="Loan purposes and barriers"),
        dict(n=4, title="Reach women-headed households", finding=clear(f, m) + " (unadjusted)", who="Lenders, MINAGRI, gender programmes",
             data=f"{f.est:.1f}% of female-headed households have a formal loan, against {m.est:.1f}% of male-headed. "
                  f"{acct_sex.loc['Female-headed'].est:.1f}% of female-headed and {acct_sex.loc['Male-headed'].est:.1f}% of "
                  "male-headed households have an account. These figures are not adjusted for wealth, farm size or land title.",
             hypothesis="That products and outreach designed for women farmers who already hold accounts would narrow the gap. "
                        "An adjusted analysis (F4, not built yet) should confirm the gap first.",
             model="", model_url="", page="who", page_label="Who gets formal credit"),
        dict(n=5, title="Connect VUP recipients to accounts", finding=clear(vy, vn) + " (FinScope, intervals understated)",
             who="MINALOC, VUP, SACCOs",
             data=f"{vy.est:.1f}% of adults in households that received a VUP cash transfer have a bank account, against "
                  f"{vn.est:.1f}% of others.",
             hypothesis="That a graduation pathway linking transfers to a SACCO account would raise account ownership and savings. "
                        "These data show the gap, not what would close it.",
             model="The graduation approach (BRAC): asset transfer, consumption support, coaching and savings; randomised trials in "
                   "six countries found lasting gains.", model_url=SRC_GRAD, page="social",
             page_label="Social protection and finance"),
        dict(n=6, title="Ease the collateral barrier for small farms", finding=clear(small, large), who="Lenders, land administration",
             data=f"Formal loans: {small.est:.1f}% on farms under 0.1 ha, {large.est:.1f}% over 1 ha. Households with titled land: "
                  f"{tit.est:.1f}%, without: {notit.est:.1f}%.",
             hypothesis="That group guarantees or titled-land alternatives would help. Farm size and land title move together with "
                        "wealth, so these are associations.",
             model="", model_url="", page="who", page_label="Who gets formal credit", other=True),
        dict(n=7, title="Use cooperatives as a channel", finding=clear(cm, nm), who="Cooperatives, lenders",
             data=f"{cm.est:.1f}% of cooperative members have a formal loan, against {nm.est:.1f}% of others; "
                  f"{nat_.loc['coop'].est:.1f}% of households belong to a cooperative."
                  + ("" if _clear(cm, nm) else " The intervals overlap, so the data cannot confirm a difference."),
             hypothesis="That bulk or group lending through cooperatives would reach more households.",
             model="", model_url="", page="who", page_label="Who gets formal credit", other=True),
    ]


def recommendations():
    T.hero(t("rec.title"), photo="farmer-beans")
    T.summary("sum.actions")
    st.markdown(
        '<p class="lede">Each idea is tied to one finding in this tool. <b>Evidence-backed</b> describes the data: the gap is clear. '
        "<b>Hypothesis</b> describes the idea: the data point that way but cannot show it would work, so test it with a small "
        "pilot first.</p>", unsafe_allow_html=True)
    cards = recommendation_cards()
    for other_ in (False, True):
        if other_:
            st.subheader("Other ideas the data allow")
        for c in [c for c in cards if c.get("other", False) == other_]:
            with st.container(border=True):
                st.subheader(f"{c['n']}. {c['title']}" if not other_ else c["title"])
                kind = "" if c["finding"].startswith("Evidence-backed") else "informal"
                st.markdown(f'<div class="fact {kind}"><span><b style="font-size:1.05rem">Finding: {c["finding"]}</b> · '
                            f'Idea: hypothesis until piloted · For: {c["who"]}</span></div>', unsafe_allow_html=True)
                st.markdown(f"**What the data show.** {c['data']}")
                st.markdown(f"**Hypothesis.** {c['hypothesis']}")
                if c["model"]:
                    st.markdown(f"**Model elsewhere.** {c['model']} [Source]({c['model_url']})")
                if c["page"] in LINKS:
                    st.page_link(LINKS[c["page"]], label=f"Figures: {c['page_label']}", icon=":material/arrow_forward:")
                else:
                    st.caption(f"Figures: {c['page_label']}")
    T.note("These are ideas drawn from group-level patterns. They are not causal findings, and this tool does not score individuals "
           "or make lending decisions. " + AHS_SRC + " Card 5 uses FinScope, whose intervals are understated (no PSU in the public file).")

