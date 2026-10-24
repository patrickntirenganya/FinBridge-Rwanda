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
from src import records as R, ussd as U
from src.i18n import t, item, lang, season_label
from ui import theme as T


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
    T.hero(t("hero.title"), t("hero.lede"), photo="farmer-weeding")
    st.subheader(t("fr.title"))
    st.markdown(f'<p class="lede">{t("fr.lede")}</p>', unsafe_allow_html=True)

    if not ss.records:
        c1, c2 = st.columns(2)
        if c1.button(t("fr.try"), type="primary", use_container_width=True):
            ss.records, ss.profile, ss.example = R.example_records(), dict(R.EXAMPLE_PROFILE), True
            st.rerun()
        up = c2.file_uploader(t("fr.load"), type="json", key="up_empty")
        if up is not None:
            _load_upload(up)
        st.info(t("fr.start"))
    elif ss.example:
        st.warning(t("fr.example_warn"))
        if st.button(t("fr.clear")):
            ss.records, ss.example = [], False
            ss.profile = dict(name="", district="", crops="", farm_ha=0.0)
            st.rerun()

    tab_add, tab_sum, tab_share = st.tabs([t("fr.tab_add"), t("fr.tab_sum"), t("fr.tab_share")])
    with tab_add:
        _add_tab(ss)
    with tab_sum:
        _summary_tab(ss)
    with tab_share:
        _share_tab(ss)
    T.note(t("fr.disclaimer"))


def _load_upload(up):
    ss = st.session_state
    try:
        prof, recs, skipped = R.parse_import(up.getvalue().decode("utf-8"))
    except Exception:
        st.error(t("fr.bad_file"))
        return
    ss.profile, ss.records, ss.example = prof, recs, False
    st.success(t("fr.loaded", n=len(recs)) + (t("fr.skipped", k=skipped) if skipped else ""))
    st.rerun()


def _add_tab(ss):
    with st.expander(t("fr.about"), expanded=not ss.profile["name"] and not ss.records):
        p = ss.profile
        c1, c2 = st.columns(2)
        p["name"] = c1.text_input(t("fr.name"), p["name"], max_chars=60)
        p["district"] = c2.text_input(t("fr.district"), p["district"], max_chars=40)
        p["crops"] = c1.text_input(t("fr.crops"), p["crops"], max_chars=60)
        p["farm_ha"] = c2.number_input(t("fr.ha"), 0.0, 10000.0, float(p["farm_ha"]), 0.1)

    kl, kmap = _opts(list(R.KINDS), lambda k: t(f"kind.{k}"))
    kind = kmap[st.radio(t("fr.what"), kl, horizontal=True)]
    with st.form("add", clear_on_submit=True):
        c1, c2 = st.columns(2)
        when = c1.date_input(t("fr.date"), date.today(), max_value=date.today())
        if kind == "expense":
            il, imap = _opts(R.EXPENSES, item)
            label = t("fr.exp_type")
        elif kind == "saving":
            il, imap, label = None, None, None
        else:
            il, imap = _opts(R.CROPS, item)
            label = t("fr.crop")
        if il:
            it = imap[c2.selectbox(label, il)]
        else:
            it = "Savings"
            c2.markdown("&nbsp;")
        qty = amt = None
        unit = "kg"
        if kind in ("harvest", "sale", "expense"):
            c1, c2 = st.columns(2)
            qty = c1.number_input(t("fr.qty"), 0.0, 1e8, 0.0, 10.0)
            ul, umap = _opts(R.UNITS, lambda u: t(f"unit.{u}"))
            unit = umap[c2.selectbox(t("fr.unit"), ul)]
        if kind != "harvest":
            amt = st.number_input(t("fr.amount"), 0, 10**10, 0, 1000)
        who = ""
        if kind in ("sale", "expense"):
            who = st.text_input(t("fr.who"), max_chars=60)
        el, emap = _opts(R.SELECTABLE_EVIDENCE, lambda k: t(f"ev.{k}"))
        ev = emap[st.radio(t("ev.title"), el, help=t("ev.help"))]
        if st.form_submit_button(t("fr.save"), type="primary"):
            rec = R.new_record(kind, when, it, float(amt) if amt else None, qty or None, unit, who, ev)
            err = R.validate(rec)
            if err:
                st.error(t(err))
            elif len(ss.records) >= R.MAX_RECORDS:
                st.error(t("fr.limit"))
            else:
                ss.records.append(rec)
                st.success(t("fr.saved"))
    if ss.records:
        st.subheader(t("fr.yours"))
        df = pd.DataFrame(ss.records).sort_values("date", ascending=False)
        df["kind"] = df.kind.map(lambda k: t(f"kind.{k}"))
        df["item"] = df["item"].map(item)
        df["unit"] = df.unit.map(lambda u: t(f"unit.{u}"))
        df["evidence"] = df.evidence.map(lambda e: t("ev.short.self") if e == "self" else t("ev.short.document"))
        st.dataframe(df[["date", "kind", "item", "quantity", "unit", "amount_rwf", "counterparty", "evidence"]]
                     .rename(columns={"date": t("fr.col.date"), "kind": t("fr.col.kind"), "item": t("fr.col.item"),
                                      "quantity": t("fr.col.qty"), "unit": t("fr.col.unit"),
                                      "amount_rwf": t("fr.col.rwf"), "counterparty": t("fr.col.with"),
                                      "evidence": t("fr.col.ev")}), hide_index=True, use_container_width=True)
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


def summary_view(records, key, lender=False):
    """Seasonal totals, visible formula, monthly chart and evidence mix. Shared by the farmer and lender pages."""
    pl, pmap = _periods(records)
    season = pmap[st.selectbox(t("fr.period"), pl, key=f"period_{key}")]
    s = R.summarise(records, season)
    m_ = lambda v: f"{v:,.0f} {t('rwf')}"
    c1, c2, c3, c4 = st.columns(4)
    with c1: T.fact(m_(s["sales"]), t("fr.k_sales"))
    with c2: T.fact(m_(s["expenses"]), t("fr.k_exp"), "informal")
    with c3: T.fact(m_(s["net"]), t("fr.k_net"), "" if s["net"] >= 0 else "gap")
    with c4: T.fact(m_(s["saved"]), t("fr.k_saved"))
    st.caption(t("ld.formula" if lender else "fr.formula"))
    if s["monthly"]:
        m = pd.DataFrame(s["monthly"]).T.fillna(0).reindex(columns=["in", "out"], fill_value=0)
        fig = go.Figure()
        fig.add_bar(x=m.index, y=m["in"], name=t("fr.chart_in"), marker_color=T.TEA)
        fig.add_bar(x=m.index, y=m["out"], name=t("fr.chart_out"), marker_color=T.SOIL)
        T.layout(fig, height=300, showlegend=True, barmode="group", legend=dict(orientation="h", y=-0.2))
        fig.update_yaxes(tickformat=",", gridcolor=T.LINE)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{t('fr.months')}** {s['months_with_records']}")
        if s["price_per_kg"]:
            st.markdown(f"**{t('ld.price' if lender else 'fr.price')}**")
            for c, v in s["price_per_kg"].items():
                st.markdown("- " + t("fr.price_row", c=item(c), v=f"{v:,.0f}"))
    with c2:
        if s["share_sold"]:
            st.markdown(f"**{t('fr.share')}**")
            for c, v in s["share_sold"].items():
                st.markdown(f"- {item(c)}: {v * 100:.0f}%")
    ev = s["evidence"]
    st.markdown(t("fr.evmix", a=ev.get("self", 0), b=ev.get("document", 0), c=ev.get("confirmed", 0)))


def _share_tab(ss):
    if not ss.records:
        st.write(t("fr.share_empty"))
        return
    st.markdown(t("fr.share_intro"))
    pl, pmap = _periods(ss.records)
    season = pmap[st.selectbox(t("fr.rep_period"), pl, key="rep_period")]
    page = R.report_html(ss.profile, ss.records, season, ss.example, lang())
    c1, c2, c3 = st.columns(3)
    c1.download_button(t("fr.dl_report"), page, "farm_record_summary.html", "text/html",
                       type="primary", use_container_width=True)
    c2.download_button(t("fr.dl_csv"), pd.DataFrame(ss.records).to_csv(index=False),
                       "farm_records.csv", "text/csv", use_container_width=True)
    c3.download_button(t("fr.dl_json"), R.export_json(ss.profile, ss.records),
                       "finbridge_backup.json", "application/json", use_container_width=True)
    st.caption(t("fr.dl_note"))
    st.info(t("fr.share_lender"))
    with st.expander(t("fr.preview")):
        st.html(page)
    up = st.file_uploader(t("fr.load_bak"), type="json", key="up_share")
    if up is not None and st.button(t("fr.replace")):
        _load_upload(up)


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
