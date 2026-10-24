"""Lender view: open the records a farmer chose to share and read them as a story with charts.

Descriptive only: no score, no verdict, no recommendation. The repayment worksheet is arithmetic on terms the
lender types in. The file is read in this browser session and never stored. Import is untrusted input, so it goes
through records.parse_import, which keeps only known fields and can never grant 'confirmed' evidence.
"""
import html
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src import records as R
from src import share
from src import vault as V
from src.i18n import t, item, lang
from ui import theme as T


def _state():
    ss = st.session_state
    ss.setdefault("lender_records", [])
    ss.setdefault("lender_profile", {})
    ss.setdefault("lender_example", False)
    return ss


def _months(first: str, last: str) -> list[str]:
    y, m = int(first[:4]), int(first[5:7])
    ey, em = int(last[:4]), int(last[5:7])
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def _show(fig, hint=None):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    if hint:
        st.caption(hint)


def _hbar(pairs, color, height=None):
    pairs = sorted(pairs, key=lambda kv: kv[1])
    fig = go.Figure(go.Bar(y=[item(k) for k, _ in pairs], x=[v for _, v in pairs], orientation="h", marker_color=color,
                           text=[f"{v:,.0f}" for _, v in pairs], textposition="outside", cliponaxis=False))
    fig.update_xaxes(tickformat=",", showgrid=False, showticklabels=False,
                     range=[0, max((v for _, v in pairs), default=1) * 1.3])
    return T.layout(fig, height=height or 90 + 44 * len(pairs))


def _glance(p, recs, ins):
    m_ = lambda v: f"{v:,.0f} {t('rwf')}"
    with st.container(border=True):
        st.markdown(f"#### {t('ld.story')}")
        for line in R.story(p, recs, lang()):
            st.markdown(f"- {line}")
    c1, c2, c3, c4 = st.columns(4)
    with c1: T.fact(m_(ins["sales"]), t("fr.k_sales"))
    with c2: T.fact(m_(ins["expenses"]), t("fr.k_exp"), "informal")
    with c3: T.fact(m_(ins["net"]), t("fr.k_net"), "" if ins["net"] >= 0 else "gap")
    with c4: T.fact(m_(ins["saved"]), t("fr.k_saved"))

    months = _months(ins["first"], ins["last"])
    mon = ins["monthly"]
    inn = [mon.get(x, {}).get("in", 0) for x in months]
    out = [mon.get(x, {}).get("out", 0) for x in months]
    st.markdown(f"**{t('ld.c_inout')}**")
    fig = go.Figure()
    fig.add_bar(x=months, y=inn, name=t("fr.chart_in"), marker_color=T.TEA)
    fig.add_bar(x=months, y=out, name=t("fr.chart_out"), marker_color=T.SOIL)
    T.layout(fig, height=300, showlegend=True, barmode="group", legend=dict(orientation="h", y=-0.2))
    fig.update_yaxes(tickformat=",", gridcolor=T.LINE)
    _show(fig, t("ld.h_inout"))

    st.markdown(f"**{t('ld.c_cum')}**")
    cum, run = [], 0.0
    for a, b in zip(inn, out):
        run += a - b
        cum.append(run)
    fig = go.Figure(go.Scatter(x=months, y=cum, mode="lines+markers", line=dict(color=T.TEA, width=3), fill="tozeroy",
                               fillcolor="rgba(47,107,79,.12)"))
    T.layout(fig, height=260)
    fig.update_yaxes(tickformat=",", gridcolor=T.LINE)
    _show(fig, t("ld.h_cum"))

    s = R.summarise(recs)
    c1, c2 = st.columns(2)
    with c1:
        if s["sales_by"]:
            st.markdown(f"**{t('ld.c_crop')}**")
            _show(_hbar(s["sales_by"].items(), T.TEA))
    with c2:
        if s["expenses_by"]:
            st.markdown(f"**{t('ld.c_exp')}**")
            _show(_hbar(s["expenses_by"].items(), T.SOIL))
    c1, c2 = st.columns(2)
    with c1:
        if s["price_per_kg"]:
            st.markdown(f"**{t('ld.c_price')}** ({t('rwf')})")
            _show(_hbar(s["price_per_kg"].items(), T.SORGHUM))
    with c2:
        if s["share_sold"]:
            st.markdown(f"**{t('ld.c_share')}**")
            _show(_hbar([(k, v * 100) for k, v in s["share_sold"].items()], T.SORGHUM))


def _worksheet(recs, ins):
    st.markdown(f"#### {t('ld.w_title')}")
    st.markdown(t("ld.w_intro"))
    c1, c2, c3 = st.columns(3)
    amt = c1.number_input(t("ld.w_amt"), 0, 10**10, 300_000, 50_000)
    term = c2.number_input(t("ld.w_term"), 1, 120, 6, 1)
    rate = c3.number_input(t("ld.w_rate"), 0.0, 100.0, 18.0, 1.0)
    inst = R.instalment(amt, rate, int(term))
    months = _months(ins["first"], ins["last"])
    nets = [ins["net_by_month"].get(x, 0.0) for x in months]
    m_ = lambda v: f"{v:,.0f} {t('rwf')}"
    st.markdown(f"**{t('ld.w_inst', i=m_(inst))}**")
    st.markdown("- " + t("ld.w_avg", m=len(months), n=m_(sum(nets) / len(months))))
    st.markdown("- " + t("ld.w_cover", k=sum(1 for n in nets if n >= inst), m=len(months)))
    st.markdown("- " + t("ld.w_total", n=m_(sum(nets)), t=m_(inst * int(term))))
    fig = go.Figure()
    fig.add_bar(x=months, y=nets, name=t("ld.w_net"), marker_color=[T.TEA if n >= 0 else T.SOIL for n in nets])
    fig.add_hline(y=inst, line=dict(color=T.SORGHUM, width=3, dash="dash"), annotation_text=t("ld.w_rep"),
                  annotation_position="top left")
    T.layout(fig, height=300)
    fig.update_yaxes(tickformat=",", gridcolor=T.LINE)
    st.markdown(f"**{t('ld.w_chart')}**")
    _show(fig)
    with st.container(border=True):
        st.markdown(f"**{t('ld.w_care')}**")
        for i in (1, 2, 3, 4):
            st.markdown(f"- {t(f'ld.w_c{i}')}")


def _quality(recs, ins):
    months = _months(ins["first"], ins["last"])
    have = set(ins["monthly"]) | {r["date"][:7] for r in recs}
    st.markdown(f"**{t('ld.c_reg')}**")
    fig = go.Figure(go.Bar(x=months, y=[1] * len(months), marker_color=[T.TEA if m in have else T.LINE for m in months],
                           hovertext=[f"{m}: {'✓' if m in have else '–'}" for m in months], hoverinfo="text"))
    T.layout(fig, height=150)
    fig.update_yaxes(visible=False)
    fig.update_layout(bargap=0.08)
    _show(fig, t("ld.h_reg"))
    ev = R.summarise(recs)["evidence"]
    st.markdown(f"**{t('ld.c_ev')}**")
    fig = go.Figure()
    for key, label, col in (("self", "ld.ev_self", T.SORGHUM), ("document", "ld.ev_doc", T.TEA), ("confirmed", "ld.ev_conf", "#8FB5A0")):
        fig.add_bar(y=[""], x=[ev.get(key, 0)], name=t(label), orientation="h", marker_color=col,
                    text=[ev.get(key, 0) or ""], textposition="inside")
    T.layout(fig, height=170, barmode="stack", showlegend=True, legend=dict(orientation="h", y=-0.6, traceorder="normal"))
    fig.update_yaxes(showticklabels=False)
    _show(fig)
    st.markdown(t("ld.chk_intro"))
    n = ins["n"]
    doc = ev.get("document", 0)
    rows = [(t("ld.chk_n"), f"{n}"), (t("ld.chk_span"), f"{ins['first']} → {ins['last']}"),
            (t("ld.chk_months"), f"{ins['months_with_records']} / {ins['span_months']}"),
            (t("ld.chk_self"), f"{ev.get('self', 0)}"), (t("ld.chk_doc"), f"{doc} ({doc / n * 100:.0f}%)"),
            (t("ld.chk_conf"), f"{ev.get('confirmed', 0)}")]
    st.table(pd.DataFrame(rows, columns=[t("ld.chk_what"), t("ld.chk_value")]).set_index(t("ld.chk_what")))
    st.markdown(f"**{t('ld.ask_title')}**")
    for i in (1, 2, 3, 4):
        st.markdown(f"- {t(f'ld.ask{i}')}")


def _entries(recs):
    df = pd.DataFrame(recs).sort_values("date", ascending=False)
    df["kind"] = df.kind.map(lambda k: t(f"kind.{k}"))
    df["item"] = df["item"].map(item)
    df["unit"] = df.unit.map(lambda u: t(f"unit.{u}"))
    df["evidence"] = df.evidence.map(lambda e: t("ev.short.self") if e == "self" else t("ev.short.document"))
    st.dataframe(df[["date", "kind", "item", "quantity", "unit", "amount_rwf", "counterparty", "evidence"]]
                 .rename(columns={"date": t("fr.col.date"), "kind": t("fr.col.kind"), "item": t("fr.col.item"),
                                  "quantity": t("fr.col.qty"), "unit": t("fr.col.unit"),
                                  "amount_rwf": t("fr.col.rwf"), "counterparty": t("fr.col.with"),
                                  "evidence": t("fr.col.ev")}), hide_index=True, use_container_width=True)


def lender_view():
    ss = _state()
    T.hero(t("ld.title"), t("ld.lede"), photo="farmer-field")

    if not ss.lender_records:
        with st.form("open_share"):
            up = st.file_uploader(t("ld.upload"), type=["fbshare", "json"])
            code = st.text_input(t("ld.code"), max_chars=20, placeholder="XXXX-XXXX-XXXX", autocomplete="off")
            org = st.text_input(t("ld.org"), max_chars=60)
            go_ = st.form_submit_button(t("ld.open"), type="primary", use_container_width=True)
        if go_:
            lock = ss.get("lender_lock") or {"fails": 0, "until": 0.0}
            left = V.wait_left(lock)
            if left:
                st.warning(t("au.wait", s=left))
            else:
                try:
                    if not (up and code):
                        raise share.ShareError
                    prof, recs, meta = share.open_package(up.getvalue().decode("utf-8"), code)
                except share.Expired:
                    st.error(t("ld.expired"))
                except Exception:
                    ss.lender_lock = V.register_fail(lock)
                    st.error(t("ld.bad"))
                else:
                    ss.lender_lock = {"fails": 0, "until": 0.0}
                    ss.lender_profile, ss.lender_records, ss.lender_example = prof, recs, False
                    ss.lender_meta = dict(meta, opened=time.strftime("%Y-%m-%d %H:%M"), org=org.strip()[:60])
                    ss.lender_skipped = 0
                    st.rerun()
        if st.button(t("ld.try")):
            ss.lender_records, ss.lender_profile, ss.lender_example = R.example_records(), dict(R.EXAMPLE_PROFILE), True
            ss.lender_meta, ss.lender_skipped = None, 0
            st.rerun()
        st.markdown(f"### {t('ld.how_title')}")
        for i in (1, 2, 3):
            st.markdown(f"{i}. {t(f'ld.how{i}')}")
        T.note(t("ld.privacy"))
        return

    p, recs = ss.lender_profile, ss.lender_records
    ins = R.insights(recs)
    if ss.lender_example:
        st.warning(t("ld.example_warn"))
    if ss.get("lender_skipped"):
        st.info(t("fr.skipped", k=ss.lender_skipped))
    ng = t("rp.none")
    e = lambda x: html.escape(str(x or ng))       # the file is untrusted: never put its text into HTML raw
    st.markdown(
        f'<div class="fact"><b>{e(p.get("name"))}</b><span>{t("rp.district")}: {e(p.get("district"))} · '
        f'{t("rp.size")}: {float(p.get("farm_ha", 0)):g} ha · {t("rp.crops")}: {e(p.get("crops"))}</span></div>',
        unsafe_allow_html=True)
    meta = ss.get("lender_meta")
    if meta:
        receipt = t("ld.receipt", t=meta["opened"] + (f" ({meta['org']})" if meta.get("org") else ""),
                    c=meta["created"], e=meta["expires"], p=meta["season"] or t("ld.all_periods"),
                    n=t("ld.names_yes" if meta["names_included"] else "ld.names_no"))
        st.caption(receipt)
        st.download_button(t("ld.receipt_dl"), receipt, "finbridge_access_receipt.txt", "text/plain")
    if st.button(t("ld.close")):
        ss.lender_records, ss.lender_profile, ss.lender_example, ss.lender_meta = [], {}, False, None
        st.rerun()

    tabs = st.tabs([t("ld.tab_glance"), t("ld.tab_loan"), t("ld.tab_quality"), t("ld.tab_rec")])
    with tabs[0]:
        _glance(p, recs, ins)
        st.download_button(t("ld.dl"), R.report_html(p, recs, None, ss.lender_example, lang()),
                           "farm_record_summary.html", "text/html")
    with tabs[1]:
        _worksheet(recs, ins)
    with tabs[2]:
        _quality(recs, ins)
    with tabs[3]:
        _entries(recs)
    T.note(t("ld.disclaimer"))
