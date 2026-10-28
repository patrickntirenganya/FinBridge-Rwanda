"""Farmer-facing pages: record tool and basic-phone (USSD) preview.

Farmer records live only in the browser session. They are never written to the server;
the farmer exports a JSON backup and can load it back later.
"""
from datetime import date
import io
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src import benchmarks as B, loanplan as LP, records as R, share, ussd as U
from src.i18n import t, item, lang, season_label
from ui import auth, theme as T


def _state():
    ss = st.session_state
    ss.setdefault("records", [])
    ss.setdefault("profile", dict(name="", district="", crops="", farm_ha=0.0))
    ss.setdefault("example", False)
    return ss


# --------------------------------------------------------------- farmer tool
def _opts(keys, label_fn):
    """Show translated labels; return (labels, label -> stored key). Stored keys stay English."""
    labels = [label_fn(k) for k in keys]
    return labels, dict(zip(labels, keys))


def _periods(records):
    seasons = R.seasons_in(records)
    labels = [t("fr.all")] + [season_label(x) for x in seasons]
    return labels, dict(zip(labels, [None] + seasons))


def my_records():
    ss = _state()
    T.hero(t("fr.title"), t("fx.welcome_b"), photo="farmer-weeding")
    if not auth.gate():
        return
    auth.account_bar()

    if not ss.records:
        st.markdown(f"### {t('fx.welcome')}")

    tab_add, tab_sum, tab_share, tab_cmp, tab_plan = st.tabs(
        [t("fr.tab_add"), t("fr.tab_sum"), t("fr.tab_share"), t("cmp.tab"), t("lp.tab")])
    with tab_add:
        _add_tab(ss)
    with tab_sum:
        _summary_tab(ss)
    with tab_share:
        _share_tab(ss)
    with tab_cmp:
        _compare_tab()
    with tab_plan:
        _plan_tab(ss)
    T.note(t("fr.disclaimer"))
    auth.persist()


KIND_ICON = {"harvest": "🌾", "sale": "💰", "expense": "🧾", "saving": "🏦", "offfarm": "🧑‍🔧"}
TILES = [("harvest", "fx.harvested"), ("sale", "fx.sold"), ("expense", "fx.spent"), ("saving", "fx.saved"), ("offfarm", "fx.offfarm")]
ITEM_ICON = {"Maize": "🌽", "Beans": "🫘", "Irish potato": "🥔", "Cassava": "🍠", "Sorghum": "🌾", "Rice": "🍚",
             "Banana": "🍌", "Coffee": "☕", "Tea": "🍃", "Vegetables": "🥬", "Milk": "🥛", "Other": "➕",
             "Seed": "🌱", "Fertiliser": "🧪", "Pesticide": "🧴", "Labour": "👷", "Transport": "🚚",
             "Equipment": "🛠️", "Land rent": "🏞️", "Loan repayment": "💳"}


def _add_tab(ss):
    """Tap what happened, tap the item, type the amount. Date, buyer and reference are optional extras."""
    with st.expander(t("fr.about"), expanded=False):
        p = ss.profile
        c1, c2 = st.columns(2)
        p["name"] = c1.text_input(t("fr.name"), p["name"], max_chars=60)
        p["district"] = c2.text_input(t("fr.district"), p["district"], max_chars=40)
        p["crops"] = c1.text_input(t("fr.crops"), p["crops"], max_chars=60)
        p["farm_ha"] = c2.number_input(t("fr.ha"), 0.0, 10000.0, float(p["farm_ha"]), 0.1)

    st.markdown(f"#### {t('fx.step1')}")
    ss.setdefault("add_kind", None)
    for col, (k, key) in zip(st.columns(len(TILES)), TILES):
        if col.button(f"{KIND_ICON[k]}  {t(key)}", key=f"tile_{k}", width="stretch",
                      type="primary" if ss.add_kind == k else "secondary"):
            ss.add_kind = k
            st.rerun()
    kind = ss.add_kind
    if not kind:
        st.info(t("fx.pick"))
    else:
        with st.form("add", clear_on_submit=True):
            keys = {"expense": R.EXPENSES, "saving": R.SAVING_PLACES, "offfarm": R.OFFFARM}.get(kind, R.CROPS)
            step_lbl = {"expense": "fx.step_exp", "saving": "fx.step_place", "offfarm": "fx.step_off"}.get(kind, "fx.step_crop")
            st.markdown(f"#### {t(step_lbl)}")
            label_of = {f"{ITEM_ICON.get(k, '')} {item(k)}": k for k in keys}
            pick = st.pills("item", list(label_of), selection_mode="single", default=list(label_of)[0],
                            label_visibility="collapsed")
            it = label_of.get(pick, "")
            qty = amt = kept = None
            if kind == "harvest":
                st.markdown(f"#### {t('fx.step_qty_h')}")
                qty = st.number_input(t("fr.qty"), 0.0, 1e8, 0.0, 10.0, label_visibility="collapsed")
                kept = st.number_input(t("fx.kept"), 0.0, 1e8, 0.0, 10.0, help=t("fx.kept_help"))
            else:
                st.markdown(f"#### {t('fx.step_amt')}")
                amt = st.number_input(t("fr.amount"), 0, 10**10, 0, 1000, label_visibility="collapsed")
                if kind == "sale":
                    qty = st.number_input(t("fx.step_qty"), 0.0, 1e8, 0.0, 10.0)
            with st.expander(t("fx.more")):
                c1, c2 = st.columns(2)
                when = c1.date_input(t("fr.date"), date.today(), max_value=date.today())
                ul, umap = _opts(R.UNITS, lambda u: t(f"unit.{u}"))
                unit = umap[c2.selectbox(t("fr.unit"), ul)]
                who = st.text_input(t("fr.who"), max_chars=60) if kind in ("sale", "expense") else ""
                ref = st.text_input(t("fx.receipt_sav" if kind == "saving" else "fx.receipt"), max_chars=R.REF_MAX,
                                    help=t("ev.help") + " " + t("fx.ref_help"))
            if st.form_submit_button(f"{KIND_ICON[kind]}  {t('fx.save')}", type="primary", width="stretch"):
                rec = R.new_record(kind, when, it, float(amt) if amt else None, qty or None, unit, who,
                                   "document" if ref.strip() else "self", retained_kg=kept or None, reference=ref)
                err = R.validate(rec)
                if err:
                    st.error(t(err))
                elif len(ss.records) >= R.MAX_RECORDS:
                    st.error(t("fr.limit"))
                else:
                    ss.records.append(rec)
                    m_ = lambda v: f"{v:,.0f} {t('rwf')}"
                    q_ = f"{qty:g} {t('unit.' + unit)}" if qty else ""
                    st.success(t(f"fx.ok_{kind}", c=item(it), a=m_(amt or 0), q=q_))
                    st.caption(t("fx.next_share"))
    if ss.records:
        st.subheader(t("fr.yours"))
        df = pd.DataFrame(ss.records).sort_values("date", ascending=False)
        df["kind"] = df.kind.map(lambda k: t(f"kind.{k}"))
        df["item"] = df["item"].map(item)
        df["unit"] = df.unit.map(lambda u: t(f"unit.{u}"))
        df["evidence"] = df.evidence.map(lambda e: t("ev.short.self") if e == "self" else t("ev.short.document"))
        df["reference"] = df["reference"].fillna("") if "reference" in df else ""
        st.dataframe(df[["date", "kind", "item", "quantity", "unit", "amount_rwf", "counterparty", "evidence", "reference"]]
                     .rename(columns={"date": t("fr.col.date"), "kind": t("fr.col.kind"), "item": t("fr.col.item"),
                                      "quantity": t("fr.col.qty"), "unit": t("fr.col.unit"),
                                      "amount_rwf": t("fr.col.rwf"), "counterparty": t("fr.col.with"),
                                      "evidence": t("fr.col.ev"), "reference": t("fr.col.ref")}), hide_index=True, width="stretch")
        ids = {r["id"]: f'{r["date"]} · {t("kind." + r["kind"])} · {item(r["item"])}' for r in ss.records}
        c1, c2 = st.columns([3, 1])
        gone = c1.selectbox(t("fr.remove_label"), list(ids), format_func=ids.get, index=None,
                            placeholder=t("fr.remove_ph"))
        if c2.button(t("fr.remove"), disabled=gone is None):
            ss.records = [r for r in ss.records if r["id"] != gone]
            st.rerun()


def _summary_tab(ss):
    if not ss.records:
        st.write(t("fr.sum_empty"))
        return
    summary_view(ss.records, "farmer")


def summary_view(records, key):
    """Plain sentence, four figures, one chart. The formulas and extra detail sit one tap away."""
    pl, pmap = _periods(records)
    season = pmap[st.selectbox(t("fr.period"), pl, key=f"period_{key}")]
    s = R.summarise(records, season)
    m_ = lambda v: f"{v:,.0f} {t('rwf')}"
    rs = [r["date"] for r in records
          if season is None or R.season_of(date.fromisoformat(r["date"])) == season]
    if rs:
        k = "fx.plain_pos" if s["net"] >= 0 else "fx.plain_neg"
        txt = t(k, a=min(rs), b=max(rs), s=m_(s["sales"]), e=m_(s["expenses"]), n=m_(abs(s["net"])))
        if s["saved"]:
            txt += " " + t("fx.plain_saved", v=m_(s["saved"]))
        st.markdown(f'<p class="lede">{txt}</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: T.fact(m_(s["sales"]), t("fr.k_sales"))
    with c2: T.fact(m_(s["expenses"]), t("fr.k_exp"), "informal")
    with c3: T.fact(m_(s["net"]), t("fr.k_net"), "" if s["net"] >= 0 else "gap")
    with c4: T.fact(m_(s["saved"]), t("fr.k_saved"))
    if s["monthly"]:
        st.markdown(f"**{t('fx.chart')}**")
        m = pd.DataFrame(s["monthly"]).T.fillna(0).reindex(columns=["in", "out"], fill_value=0)
        fig = go.Figure()
        fig.add_bar(x=m.index, y=m["in"], name=t("fr.chart_in"), marker_color=T.TEA)
        fig.add_bar(x=m.index, y=m["out"], name=t("fr.chart_out"), marker_color=T.SOIL)
        T.layout(fig, height=280, showlegend=True, barmode="group", legend=dict(orientation="h", y=-0.2))
        fig.update_yaxes(tickformat=",", gridcolor=T.LINE)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    with st.expander(t("fx.details")):
        st.caption(t("fr.formula"))
        st.markdown(f"**{t('fr.months')}** {s['months_with_records']}")
        if s["price_per_kg"]:
            st.markdown(f"**{t('fr.price')}**")
            for c, v in s["price_per_kg"].items():
                st.markdown("- " + t("fr.price_row", c=item(c), v=f"{v:,.0f}"))
        if s["share_sold"]:
            st.markdown(f"**{t('fr.share')}**")
            for c, v in s["share_sold"].items():
                st.markdown(f"- {item(c)}: {v * 100:.0f}%")
        ev = s["evidence"]
        st.markdown(t("fr.evmix", a=ev.get("self", 0), b=ev.get("document", 0), c=ev.get("confirmed", 0)))


def _compare_tab():
    """How one harvest compares with similar plots. Computed here, shown here, never added to a record or export."""
    st.markdown(f'<p class="lede">{t("cmp.lede")}</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cl, cmap = _opts(B.crops(), lambda c: t(f"cmp.crop.{c}"))
    crop = cmap[c1.selectbox(t("cmp.crop"), cl, key="cmp_crop")]
    sl, smap = _opts(B.seasons_for(crop), lambda x: t(f"cmp.season.{x}"))
    season = smap[c2.selectbox(t("cmp.season"), sl, key="cmp_season")]
    c3, c4 = st.columns(2)
    kg = c3.number_input(t("cmp.kg"), 0.0, 1e8, 0.0, 10.0, key="cmp_kg")
    area = c4.number_input(t("cmp.area"), 0.0, 1e6, 0.0, 0.01, key="cmp_area")
    ul, umap = _opts(["ha", "m2"], lambda u: t(f"cmp.unit.{u}"))
    unit = umap[c4.radio(t("cmp.area_unit"), ul, horizontal=True, key="cmp_unit", label_visibility="collapsed")]
    share = st.slider(t("cmp.share"), 10, 100, 100, 5, key="cmp_share")
    st.caption(t("cmp.share_hint"))
    res = B.band(crop, season, kg, area * (10000 if unit == "ha" else 1), share)
    if not res:
        st.info(t("cmp.enter"))
        return
    st.markdown(f"#### {t('cmp.' + res['band'])}")
    st.markdown(t("cmp.range", y=f"{res['yield_kg_ha']:,}", a=f"{res['p25']:,}", m=f"{res['p50']:,}", b=f"{res['p75']:,}"))
    if res["band"] == B.BELOW:
        st.info(t("cmp.below_help"))
    st.caption(t("cmp.foot", src=res["source"]) + " " + t("cmp.not_saved"))


ITEM_ROWS = 5


def _plan_tab(ss):
    """Loan purpose sheet: a clear plan for a SACCO officer. Saved in the profile (encrypted with the records)."""
    st.markdown(f"#### {t('lp.title')}")
    st.markdown(f'<p class="lede">{t("lp.lede")}</p>', unsafe_allow_html=True)
    cur = ss.profile.get("loan_plan") or dict(LP.EMPTY)
    with st.form("loan_plan"):
        pl, pmap = _opts(LP.PURPOSES, lambda k: t(f"lp.p_{k}"))
        pick = st.radio(t("lp.purpose"), pl, index=LP.PURPOSES.index(cur["purpose"]) if cur["purpose"] in LP.PURPOSES else None,
                        horizontal=True, key="lp_purpose")
        other = st.text_input(t("lp.other"), cur.get("purpose_other", ""), max_chars=40, key="lp_other")
        st.markdown(f"**{t('lp.items')}**")
        rows = []
        for i in range(ITEM_ROWS):
            it = cur["items"][i] if i < len(cur["items"]) else {}
            c1, c2, c3 = st.columns([3, 1, 1])
            name = c1.text_input(t("lp.item"), it.get("item", ""), max_chars=40, key=f"lp_item{i}", label_visibility="collapsed" if i else "visible")
            qty = c2.number_input(t("lp.qty"), 0.0, 1e8, float(it.get("qty") or 0), 1.0, key=f"lp_qty{i}", label_visibility="collapsed" if i else "visible")
            unit = c3.text_input(t("lp.unit"), it.get("unit", ""), max_chars=12, key=f"lp_unit{i}", label_visibility="collapsed" if i else "visible")
            rows.append(dict(item=name, qty=qty or None, unit=unit))
        cost = st.number_input(t("lp.cost"), 0, 10**10, int(cur.get("cost_rwf") or 0), 5000, key="lp_cost")
        mkeys = [None] + list(range(1, 13))
        ml, mmap = _opts(mkeys, lambda m: t("lp.none_month") if m is None else t(f"lp.m{m}"))
        c1, c2 = st.columns(2)
        pm = mmap[c1.selectbox(t("lp.plant"), ml, index=mkeys.index(cur.get("plant_month")), key="lp_plant")]
        hm = mmap[c2.selectbox(t("lp.harvest"), ml, index=mkeys.index(cur.get("harvest_month")), key="lp_harvest")]
        rl, rmap = _opts(LP.REPAY, lambda k: t(f"lp.r_{k}"))
        repay = st.pills(t("lp.repay"), rl, selection_mode="multi", default=[t(f"lp.r_{k}") for k in cur["repay"]], key="lp_repay")
        gl, gmap = _opts(LP.GROUPS, lambda k: t(f"lp.g_{k}"))
        groups = st.pills(t("lp.groups"), gl, selection_mode="multi", default=[t(f"lp.g_{k}") for k in cur["groups"]], key="lp_groups")
        go_ = st.form_submit_button(t("lp.save"), type="primary", width="stretch")
    if go_:
        plan = LP.sanitize(dict(purpose=pmap.get(pick, ""), purpose_other=other, items=rows, cost_rwf=cost or None,
                                plant_month=pm, harvest_month=hm, repay=[rmap[x] for x in repay or []],
                                groups=[gmap[x] for x in groups or []]))
        err = LP.validate(plan) if plan else "lp.v_purpose"
        if err:
            st.error(t(err))
        else:
            ss.profile["loan_plan"] = plan
            st.success(t("lp.saved"))
    plan = ss.profile.get("loan_plan")
    if plan:
        page = LP.plan_html(ss.profile, plan, lang(), ss.example)
        c1, c2 = st.columns(2)
        c1.download_button(t("lp.dl"), page, "loan_plan.html", "text/html", width="stretch")
        if c2.button(t("lp.clear"), width="stretch"):
            ss.profile.pop("loan_plan", None)
            st.rerun()
        with st.expander(t("lp.preview")):
            st.html(page)
    T.note(t("lp.note"))


def _share_tab(ss):
    if not ss.records:
        st.write(t("fr.share_empty"))
        return
    pl, pmap = _periods(ss.records)
    season = pmap[st.selectbox(t("fr.rep_period"), pl, key="rep_period")]

    st.markdown(f"#### {t('sh.title')}")
    st.markdown(t("sh.intro"))
    c1, c2 = st.columns(2)
    names = c1.checkbox(t("sh.names"), value=False)
    mine = c2.checkbox(t("sh.myname"), value=True)
    has_plan = bool(ss.profile.get("loan_plan"))
    with_plan = st.checkbox(t("lp.share"), value=False, disabled=not has_plan, key="share_plan",
                            help=None if has_plan else t("lp.share_none"))
    vkeys = list(share.VALIDITY_HOURS)
    vlabels = {k: t(f"sh.v{k}") for k in vkeys}
    valid = st.radio(t("sh.valid"), vkeys, index=1, horizontal=True, format_func=vlabels.get)
    if st.button(t("sh.make"), type="primary", width="stretch"):
        try:
            pkg, code = share.make_package(ss.profile, ss.records, season=season, include_names=names,
                                           include_farmer_name=mine, include_plan=with_plan and has_plan, validity=valid)
        except share.ShareError:
            st.error(t("sh.none"))
        else:
            ss["last_share"] = dict(pkg=pkg, code=code, valid=valid)
    ls = ss.get("last_share")
    if ls:
        with st.container(border=True):
            st.markdown(f"**{t('sh.code')}**")
            st.code(ls["code"], language=None)
            st.caption(t("sh.code_note"))
            st.download_button(t("sh.dl"), ls["pkg"], "finbridge_share.fbshare", "application/json",
                               type="primary", width="stretch")
            st.caption(t("sh.limit"))

    st.markdown(f"#### {t('sh.plain')}")
    st.markdown(t("fr.share_intro"))
    page = R.report_html(ss.profile, ss.records, season, ss.example, lang())
    c1, c2 = st.columns(2)
    c1.download_button(t("fr.dl_report"), page, "farm_record_summary.html", "text/html", width="stretch")
    c2.download_button(t("fr.dl_csv"), pd.DataFrame(ss.records).to_csv(index=False),
                       "farm_records.csv", "text/csv", width="stretch")
    st.caption(t("fr.dl_note"))
    with st.expander(t("fr.preview")):
        st.html(page)

    if auth.signed_in() and ss.get("blob"):
        st.markdown("#### " + t("au.backup_dl"))
        st.download_button(t("au.backup_dl"), ss["blob"], "finbridge_backup.fbvault", "application/json",
                           width="stretch")
        st.caption(t("au.backup_note"))


# --------------------------------------------------------- feature-phone view
def phone_preview():
    ss = _state()
    lg = lang()
    T.hero(t("us.title"), photo="hands-phone")
    st.markdown(f'<p class="lede">{t("us.lede")}</p>', unsafe_allow_html=True)
    u = st.session_state.setdefault("ussd", {"state": {}, "screen": None, "ended": False})
    if u["screen"] is None or u.get("lg") != lg:       # restart the menu when the language changes
        u.update(state={}, screen=U.menu(lg), ended=False, lg=lg)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown(f'<div style="background:#1C2B24;color:#E8F0EA;font-family:monospace;padding:1rem;'
                    f'border-radius:12px;white-space:pre-wrap;min-height:220px;max-width:340px">'
                    f'{u["screen"]}</div>', unsafe_allow_html=True)
        with st.form("ussd_in", clear_on_submit=True):
            txt = st.text_input(t("us.reply"), max_chars=12, label_visibility="collapsed",
                                placeholder=t("us.reply_ph"))
            send = st.form_submit_button(t("us.send"))
        if send and txt and not u["ended"]:
            scr, stt, end = U.step(u["state"], txt, ss.records, lg=lg)
            u.update(state=stt, screen=scr, ended=end)
            st.rerun()
        if st.button(t("us.dial")):
            u.update(state={}, screen=U.menu(lg), ended=False)
            st.rerun()
    with c2:
        st.markdown(t("us.try"))
        s = R.summarise(ss.records)
        m_ = lambda v: f"{v:,.0f} {t('rwf')}"
        st.markdown(t("us.saved", n=s["n"], s=m_(s["sales"]), e=m_(s["expenses"])))
        st.caption(t("us.appear"))
    T.note(t("us.note"))
