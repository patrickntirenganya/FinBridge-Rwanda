"""Lender view: open the records a farmer chose to share. Descriptive only: no score, no recommendation.

The file is read in this browser session and never stored. Import is untrusted input, so it goes through
records.parse_import, which keeps only known fields and can never grant 'confirmed' evidence.
"""
import pandas as pd
import streamlit as st
from src import records as R
from src.i18n import t, item, lang
from ui import theme as T
from ui.farmer import summary_view


def _state():
    ss = st.session_state
    ss.setdefault("lender_records", [])
    ss.setdefault("lender_profile", {})
    ss.setdefault("lender_example", False)
    return ss


def _checks(records):
    """Plain counts a lender can verify by eye. None of these is a score."""
    ev = R.summarise(records)["evidence"]
    n = len(records)
    dates = sorted(r["date"] for r in records)
    months = len({d[:7] for d in dates})
    doc = ev.get("document", 0)
    return [
        (t("ld.chk_n"), f"{n}"),
        (t("ld.chk_span"), f"{dates[0]} → {dates[-1]}" if dates else "-"),
        (t("ld.chk_months"), f"{months}"),
        (t("ld.chk_self"), f"{ev.get('self', 0)}"),
        (t("ld.chk_doc"), f"{doc} ({doc / n * 100:.0f}%)" if n else "0"),
        (t("ld.chk_conf"), f"{ev.get('confirmed', 0)}"),
    ]


def lender_view():
    ss = _state()
    T.hero(t("ld.title"), t("ld.lede"), photo="farmer-field")

    if not ss.lender_records:
        c1, c2 = st.columns(2)
        up = c1.file_uploader(t("ld.upload"), type="json", key="ld_up")
        if up is not None:
            try:
                prof, recs, skipped = R.parse_import(up.getvalue().decode("utf-8"))
            except Exception:
                st.error(t("fr.bad_file"))
            else:
                if not recs:
                    st.error(t("ld.empty"))
                else:
                    ss.lender_profile, ss.lender_records, ss.lender_example = prof, recs, False
                    ss.lender_skipped = skipped
                    st.rerun()
        c2.markdown(f"<p class='note'>{t('ld.example_hint')}</p>", unsafe_allow_html=True)
        if c2.button(t("ld.try"), type="primary", use_container_width=True):
            ss.lender_records, ss.lender_profile, ss.lender_example = R.example_records(), dict(R.EXAMPLE_PROFILE), True
            ss.lender_skipped = 0
            st.rerun()
        st.markdown(f"### {t('ld.how_title')}")
        for i in (1, 2, 3):
            st.markdown(f"{i}. {t(f'ld.how{i}')}")
        T.note(t("ld.privacy"))
        return

    p, recs = ss.lender_profile, ss.lender_records
    if ss.lender_example:
        st.warning(t("ld.example_warn"))
    if ss.get("lender_skipped"):
        st.info(t("fr.skipped", k=ss.lender_skipped))
    ng = t("rp.none")
    st.markdown(
        f'<div class="fact"><b>{p.get("name") or ng}</b><span>{t("rp.district")}: {p.get("district") or ng} · '
        f'{t("rp.size")}: {p.get("farm_ha", 0):g} ha · {t("rp.crops")}: {p.get("crops") or ng}</span></div>',
        unsafe_allow_html=True)
    if st.button(t("ld.close")):
        ss.lender_records, ss.lender_profile, ss.lender_example = [], {}, False
        st.rerun()

    tab_sum, tab_det, tab_rec, tab_chk = st.tabs([t("ld.tab_sum"), t("ld.tab_det"), t("ld.tab_rec"), t("ld.tab_chk")])
    with tab_sum:
        summary_view(recs, "lender", lender=True)
        st.download_button(t("ld.dl"), R.report_html(p, recs, None, ss.lender_example, lang()),
                           "farm_record_summary.html", "text/html")
    with tab_det:
        s = R.summarise(recs)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{t('rp.by_crop')}**")
            st.dataframe(pd.DataFrame([(item(k), v) for k, v in sorted(s["sales_by"].items(), key=lambda kv: -kv[1])],
                                      columns=[t("fr.col.item"), t("fr.col.rwf")]), hide_index=True)
            if s["price_per_kg"]:
                st.markdown(f"**{t('ld.price')}**")
                for c, v in s["price_per_kg"].items():
                    st.markdown("- " + t("fr.price_row", c=item(c), v=f"{v:,.0f}"))
        with c2:
            st.markdown(f"**{t('rp.by_exp')}**")
            st.dataframe(pd.DataFrame([(item(k), v) for k, v in sorted(s["expenses_by"].items(), key=lambda kv: -kv[1])],
                                      columns=[t("fr.col.item"), t("fr.col.rwf")]), hide_index=True)
            if s["share_sold"]:
                st.markdown(f"**{t('fr.share')}**")
                for c, v in s["share_sold"].items():
                    st.markdown(f"- {item(c)}: {v * 100:.0f}%")
    with tab_rec:
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
    with tab_chk:
        st.markdown(t("ld.chk_intro"))
        st.table(pd.DataFrame(_checks(recs), columns=[t("ld.chk_what"), t("ld.chk_value")]).set_index(t("ld.chk_what")))
        st.markdown(f"**{t('ld.ask_title')}**")
        for i in (1, 2, 3, 4):
            st.markdown(f"- {t(f'ld.ask{i}')}")
    T.note(t("ld.disclaimer"))
