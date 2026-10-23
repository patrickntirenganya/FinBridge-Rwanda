"""USSD menu as a pure state machine (same record engine as the web page).

A real deployment would sit behind a telecom/aggregator USSD gateway; this module has no
network code, so it can be unit-tested and shown in a simulator. Screens stay under 160
characters, the usual USSD limit.
"""
from __future__ import annotations
from datetime import date
from src import records as R
from src.i18n import t

SALE_CROPS = ["Maize", "Beans", "Irish potato", "Cassava", "Other"]
EXP_TYPES = ["Seed", "Fertiliser", "Labour", "Transport", "Other"]


def menu(lg="rw"):
    return t("u.menu", lg)


def _list(title, options, lg):
    from src.i18n import item
    return title + "\n" + "\n".join(f"{i + 1} {item(o, lg)}" for i, o in enumerate(options))


def step(state: dict, text: str, records: list[dict], today: date | None = None, lg: str = "rw"):
    """Advance one USSD screen. Returns (screen_text, new_state, ended).
    `records` is mutated when a record is saved. Stored items stay English keys."""
    today = today or date.today()
    s = dict(state or {})
    tt = text.strip()
    stage = s.get("stage", "menu")
    T_ = lambda k, **kw: t(k, lg, **kw)

    def back(msg=""):
        return (msg + ("\n" if msg else "") + menu(lg), {"stage": "menu"}, False)

    if stage == "menu":
        if tt == "1": return _list(T_("u.sale_crop"), SALE_CROPS, lg), {"stage": "pick", "kind": "sale", "opts": SALE_CROPS}, False
        if tt == "2": return _list(T_("u.exp_type"), EXP_TYPES, lg), {"stage": "pick", "kind": "expense", "opts": EXP_TYPES}, False
        if tt == "3": return _list(T_("u.harv_crop"), SALE_CROPS, lg), {"stage": "pick", "kind": "harvest", "opts": SALE_CROPS}, False
        if tt == "4": return T_("u.saved_amt"), {"stage": "amount", "kind": "saving", "item": "Savings"}, False
        if tt == "5":
            sm = R.summarise(records)
            return (T_("u.summary", s=f"{sm['sales']:,.0f}", e=f"{sm['expenses']:,.0f}",
                       n=f"{sm['net']:,.0f}", v=f"{sm['saved']:,.0f}"), {"stage": "summary"}, False)
        if tt == "0": return T_("u.bye"), {}, True
        return back(T_("u.choose"))
    if stage == "summary":
        return back()
    if stage == "pick":
        opts = s["opts"]
        if not (tt.isdigit() and 1 <= int(tt) <= len(opts)):
            return _list(T_("u.pick"), opts, lg), s, False
        s["item"] = opts[int(tt) - 1]
        if s["kind"] == "harvest":
            return T_("u.kg_harv"), {**s, "stage": "qty"}, False
        return T_("u.amount"), {**s, "stage": "amount"}, False
    if stage in ("qty", "amount"):
        try:
            v = float(tt.replace(",", ""))
            if v <= 0: raise ValueError
        except ValueError:
            return T_("u.num"), s, False
        if stage == "qty":
            rec = R.new_record("harvest", today, s["item"], quantity=v, unit="kg")
            return _save(rec, records, back, lg)
        if s["kind"] == "sale":
            return T_("u.kg_sold"), {**s, "stage": "salekg", "amount": v}, False
        rec = R.new_record(s["kind"], today, s["item"], amount_rwf=v)
        return _save(rec, records, back, lg)
    if stage == "salekg":
        try:
            kg = float(tt.replace(",", "")); assert kg >= 0
        except Exception:
            return T_("u.num_skip"), s, False
        rec = R.new_record("sale", today, s["item"], amount_rwf=s["amount"], quantity=kg or None, unit="kg")
        return _save(rec, records, back, lg)
    return back()


def _save(rec, records, back, lg):
    err = R.validate(rec)
    if err:
        return back(t(err, lg))
    records.append(rec)
    return back(t("u.saved", lg))
