"""Farmer record engine: channel-agnostic (web page, USSD simulator, future SMS).

A record is one dict:
    id, date (ISO), kind, item, quantity (float|None), unit, amount_rwf (float|None),
    counterparty (str), evidence

Design rules
  * Nothing is scored. The summary only adds up what the farmer recorded, and every
    figure is shown with its formula.
  * Evidence is never upgraded by the system. "self" = farmer's own entry.
    "document" = farmer says they hold a receipt or mobile-money message (not checked).
    "confirmed" is reserved for a future buyer/cooperative verification step.
  * Data stays with the farmer: export/import as JSON; the app stores nothing server-side.
"""
from __future__ import annotations
import html
import json
import uuid
from datetime import date, datetime
from collections import defaultdict

KINDS = {"harvest": "Harvest", "sale": "Sale", "expense": "Expense", "saving": "Saving"}
EVIDENCE = {"self": "Self-reported",
            "document": "Receipt or mobile-money message held (not checked)",
            "confirmed": "Confirmed by buyer or cooperative"}
SELECTABLE_EVIDENCE = ["self", "document"]       # "confirmed" needs a verifier (future)
CROPS = ["Maize", "Beans", "Irish potato", "Cassava", "Sorghum", "Rice", "Banana", "Coffee",
         "Tea", "Vegetables", "Milk", "Other"]
EXPENSES = ["Seed", "Fertiliser", "Pesticide", "Labour", "Transport", "Equipment", "Land rent",
            "Loan repayment", "Other"]
UNITS = ["kg", "litres", "count"]
MAX_RECORDS = 2000


def season_of(d: date) -> str:
    """Rwanda's agricultural seasons: A Sep-Jan, B Feb-Jun, C Jul-Aug."""
    if d.month in (9, 10, 11, 12):
        return f"Season A {d.year}/{str(d.year + 1)[2:]}"
    if d.month == 1:
        return f"Season A {d.year - 1}/{str(d.year)[2:]}"
    if d.month <= 6:
        return f"Season B {d.year}"
    return f"Season C {d.year}"


def new_record(kind, d, item, amount_rwf=None, quantity=None, unit="kg", counterparty="",
               evidence="self") -> dict:
    return dict(id=uuid.uuid4().hex[:8], date=d.isoformat() if isinstance(d, date) else str(d),
                kind=kind, item=item, quantity=quantity, unit=unit, amount_rwf=amount_rwf,
                counterparty=counterparty.strip()[:60], evidence=evidence)


def validate(r: dict) -> str | None:
    """Return an i18n message key (see src/i18n.py) if the record is invalid, else None."""
    try:
        datetime.strptime(r["date"], "%Y-%m-%d")
    except Exception:
        return "v.date"
    if r["kind"] not in KINDS:
        return "v.kind"
    if r["evidence"] not in EVIDENCE:
        return "v.ev"
    if r["kind"] in ("sale", "expense", "saving") and not (r.get("amount_rwf") or 0) > 0:
        return "v.amount"
    if r["kind"] == "harvest" and not (r.get("quantity") or 0) > 0:
        return "v.harvest"
    if r.get("amount_rwf") is not None and not 0 <= r["amount_rwf"] <= 1e10:
        return "v.big_amount"
    if r.get("quantity") is not None and not 0 <= r["quantity"] <= 1e8:
        return "v.big_qty"
    if not str(r.get("item", "")).strip():
        return "v.item"
    return None


def parse_import(text: str) -> tuple[dict, list[dict], int]:
    """Read a JSON backup. Untrusted input: only known fields and types are kept.
    Returns (profile, records, rows_skipped)."""
    data = json.loads(text)
    prof_in = data.get("profile", {}) if isinstance(data, dict) else {}
    profile = {k: str(prof_in.get(k, ""))[:80] for k in ("name", "district", "crops")}
    try:
        profile["farm_ha"] = max(0.0, min(1e4, float(prof_in.get("farm_ha", 0))))
    except (TypeError, ValueError):
        profile["farm_ha"] = 0.0
    rows = data.get("records", []) if isinstance(data, dict) else []
    keep, skipped = [], 0
    for x in rows[:MAX_RECORDS]:
        try:
            r = dict(id=str(x.get("id", uuid.uuid4().hex[:8]))[:12], date=str(x["date"]),
                     kind=str(x["kind"]), item=str(x["item"])[:40],
                     quantity=None if x.get("quantity") is None else float(x["quantity"]),
                     unit=str(x.get("unit", "kg")) if x.get("unit") in UNITS else "kg",
                     amount_rwf=None if x.get("amount_rwf") is None else float(x["amount_rwf"]),
                     counterparty=str(x.get("counterparty", ""))[:60],
                     evidence=str(x.get("evidence", "self")))
            if r["evidence"] == "confirmed":      # only a verifier may set this; never trust a file
                r["evidence"] = "document"
        except Exception:
            skipped += 1
            continue
        if validate(r):
            skipped += 1
        else:
            keep.append(r)
    return profile, keep, skipped + max(0, len(rows) - MAX_RECORDS)


def export_json(profile: dict, records: list[dict]) -> str:
    return json.dumps({"app": "FinBridge", "version": 1, "profile": profile, "records": records},
                      indent=1, ensure_ascii=False)


def summarise(records: list[dict], season: str | None = None) -> dict:
    """Add up what was recorded. `season` filters to one season label; None = everything."""
    rs = [r for r in records
          if season is None or season_of(datetime.strptime(r["date"], "%Y-%m-%d").date()) == season]
    tot = defaultdict(float)
    sales_by, exp_by, harv_kg, sold_kg = defaultdict(float), defaultdict(float), defaultdict(float), defaultdict(float)
    months, monthly = set(), defaultdict(lambda: defaultdict(float))
    ev = defaultdict(int)
    for r in rs:
        m = r["date"][:7]
        months.add(m)
        ev[r["evidence"]] += 1
        a = r.get("amount_rwf") or 0
        if r["kind"] == "sale":
            tot["sales"] += a; sales_by[r["item"]] += a; monthly[m]["in"] += a
            if r["unit"] == "kg" and r.get("quantity"):
                sold_kg[r["item"]] += r["quantity"]
        elif r["kind"] == "expense":
            tot["expenses"] += a; exp_by[r["item"]] += a; monthly[m]["out"] += a
        elif r["kind"] == "saving":
            tot["saved"] += a
        elif r["kind"] == "harvest" and r["unit"] == "kg":
            harv_kg[r["item"]] += r.get("quantity") or 0
    price = {c: sales_by[c] / sold_kg[c] for c in sold_kg if sold_kg[c] > 0 and sales_by[c] > 0}
    share_sold = {c: min(1.0, sold_kg[c] / harv_kg[c]) for c in harv_kg if harv_kg[c] > 0 and c in sold_kg}
    return dict(n=len(rs), sales=tot["sales"], expenses=tot["expenses"],
                net=tot["sales"] - tot["expenses"], saved=tot["saved"],
                sales_by=dict(sales_by), expenses_by=dict(exp_by), harvest_kg=dict(harv_kg),
                price_per_kg=price, share_sold=share_sold,
                months_with_records=len(months), evidence=dict(ev),
                monthly={k: dict(v) for k, v in sorted(monthly.items())})


def _month_span(first: str, last: str) -> int:
    a, b = datetime.strptime(first, "%Y-%m-%d"), datetime.strptime(last, "%Y-%m-%d")
    return (b.year - a.year) * 12 + (b.month - a.month) + 1


def insights(records: list[dict]) -> dict:
    """Plain facts a lender can read at a glance, all derived from the farmer's own entries. Nothing is scored."""
    if not records:
        return {}
    s = summarise(records)
    dates = sorted(r["date"] for r in records)
    span = _month_span(dates[0], dates[-1])
    sale_months = {r["date"][:7] for r in records if r["kind"] == "sale" and (r.get("amount_rwf") or 0) > 0}
    net_by_month = {}
    for m, v in s["monthly"].items():
        net_by_month[m] = v.get("in", 0) - v.get("out", 0)
    sales = sorted(((r.get("amount_rwf") or 0, r["item"], r["date"]) for r in records if r["kind"] == "sale"), reverse=True)
    top_crop = max(s["sales_by"].items(), key=lambda kv: kv[1]) if s["sales_by"] else None
    top_exp = max(s["expenses_by"].items(), key=lambda kv: kv[1]) if s["expenses_by"] else None
    n = len(records)
    ev = s["evidence"]
    return dict(
        first=dates[0], last=dates[-1], span_months=span, months_with_records=s["months_with_records"],
        sale_months=len(sale_months), sales=s["sales"], expenses=s["expenses"], net=s["net"], saved=s["saved"],
        top_crop=top_crop and (top_crop[0], top_crop[1] / s["sales"] if s["sales"] else 0),
        top_expense=top_exp and (top_exp[0], top_exp[1] / s["expenses"] if s["expenses"] else 0),
        biggest_sale=sales[0] if sales and sales[0][0] > 0 else None,
        receipt_share=(ev.get("document", 0) + ev.get("confirmed", 0)) / n,
        n=n, net_by_month=net_by_month, monthly=s["monthly"])


def instalment(principal: float, annual_rate_pct: float, months: int) -> float:
    """Level monthly repayment of a loan (annuity formula). Pure arithmetic for a lender's own what-if."""
    if months <= 0 or principal <= 0:
        return 0.0
    r = annual_rate_pct / 100 / 12
    return principal / months if r == 0 else principal * r / (1 - (1 + r) ** -months)


def story(profile: dict, records: list[dict], lg: str = "en") -> list[str]:
    """The farmer's records told as short plain sentences, one fact each. Facts only: no judgement, no advice."""
    from src.i18n import t, item
    T_ = lambda key, **kw: t(key, lg, **kw)
    i = insights(records)
    if not i:
        return []
    money = lambda v: f"{v:,.0f} {T_('rwf')}"
    out = []
    who = (profile.get("name") or "").strip()
    place = (profile.get("district") or "").strip()
    crops = (profile.get("crops") or "").strip()
    ha = profile.get("farm_ha") or 0
    if who or place or crops or ha:
        out.append(T_("st.who", who=who or T_("st.farmer"), ha=f"{ha:g}", place=place or "-", crops=crops or "-"))
    out.append(T_("st.span", a=i["first"], b=i["last"], m=i["span_months"], k=i["months_with_records"]))
    out.append(T_("st.totals", s=money(i["sales"]), e=money(i["expenses"]), n=money(i["net"])))
    if i["top_crop"]:
        out.append(T_("st.top_crop", c=item(i["top_crop"][0], lg), p=f"{i['top_crop'][1] * 100:.0f}"))
    if i["top_expense"]:
        out.append(T_("st.top_exp", c=item(i["top_expense"][0], lg), p=f"{i['top_expense'][1] * 100:.0f}"))
    if i["sale_months"]:
        out.append(T_("st.sale_months", k=i["sale_months"], m=i["span_months"]))
    if i["saved"] > 0:
        out.append(T_("st.saved", v=money(i["saved"])))
    out.append(T_("st.receipts", p=f"{i['receipt_share'] * 100:.0f}"))
    return out


def seasons_in(records: list[dict]) -> list[str]:
    seen = {season_of(datetime.strptime(r["date"], "%Y-%m-%d").date()) for r in records}
    return sorted(seen, reverse=True)


def rwf(x: float) -> str:
    return f"{x:,.0f} RWF"


def report_html(profile: dict, records: list[dict], season: str | None, example: bool = False,
                lg: str = "en") -> str:
    """A plain, printable summary the farmer can show a lender. Escapes all user text."""
    from src.i18n import t, item, season_label
    T_ = lambda k, **kw: t(k, lg, **kw)
    s = summarise(records, season)
    e = html.escape
    scope = season_label(season, lg) if season else T_("fr.all")
    ev = s["evidence"]
    none = f"<tr><td colspan=2>{T_('rp.none_rec')}</td></tr>"
    cur = T_("rwf")
    money = lambda v: f"{v:,.0f} {cur}"
    rows = "".join(f"<tr><td>{e(item(c, lg))}</td><td>{money(v)}</td></tr>" for c, v in
                   sorted(s["sales_by"].items(), key=lambda kv: -kv[1])) or none
    exp = "".join(f"<tr><td>{e(item(c, lg))}</td><td>{money(v)}</td></tr>" for c, v in
                  sorted(s["expenses_by"].items(), key=lambda kv: -kv[1])) or none
    mon = "".join(f"<tr><td>{e(m)}</td><td>{money(v.get('in', 0))}</td><td>{money(v.get('out', 0))}</td></tr>"
                  for m, v in s["monthly"].items())
    banner = (f'<p style="background:#C2922A;color:#fff;padding:8px"><b>{T_("rp.example")}</b></p>'
              if example else "")
    ng = T_("rp.none")
    return f"""<!doctype html><html lang="{lg}"><meta charset="utf-8"><title>{T_('rp.title')}</title>
<body style="font-family:Atkinson Hyperlegible,Segoe UI,sans-serif;max-width:720px;margin:2rem auto;color:#1C2B24">
{banner}<h1>{T_('rp.title')}</h1>
<p>{T_('rp.farmer')}: <b>{e(profile.get('name') or ng)}</b> · {T_('rp.district')}: {e(profile.get('district') or ng)}
 · {T_('rp.size')}: {profile.get('farm_ha', 0):g} ha · {T_('rp.crops')}: {e(profile.get('crops') or ng)}</p>
<p>{T_('rp.period')}: <b>{e(scope)}</b> · {T_('rp.generated')} {date.today().isoformat()}</p>
<div style="border-left:4px solid #8E3B2E;padding:6px 12px;background:#EEF2EC">
<b>{T_('rp.read')}</b> {T_('rp.warn')}
{T_('rp.entries', a=ev.get('self', 0), b=ev.get('document', 0), c=ev.get('confirmed', 0))}</div>
<h2>{T_('rp.totals')}</h2><table cellpadding=6>
<tr><td>{T_('rp.sales')}</td><td><b>{money(s['sales'])}</b></td></tr>
<tr><td>{T_('rp.exp')}</td><td><b>{money(s['expenses'])}</b></td></tr>
<tr><td>{T_('rp.net')}</td><td><b>{money(s['net'])}</b></td></tr>
<tr><td>{T_('rp.saved')}</td><td><b>{money(s['saved'])}</b></td></tr>
<tr><td>{T_('rp.months')}</td><td><b>{s['months_with_records']}</b></td></tr></table>
<p style="font-size:.9rem">{T_('rp.formula')}</p>
<h2>{T_('rp.by_crop')}</h2><table cellpadding=6>{rows}</table>
<h2>{T_('rp.by_exp')}</h2><table cellpadding=6>{exp}</table>
<h2>{T_('rp.by_month')}</h2><table cellpadding=6><tr><th>{T_('rp.month')}</th><th>{T_('rp.in')}</th><th>{T_('rp.out')}</th></tr>{mon}</table>
<p style="font-size:.85rem">{T_('rp.footer')}</p>
</body></html>"""


EXAMPLE_PROFILE = dict(name="Example farmer", district="Huye", crops="Maize, beans", farm_ha=0.6)


def example_records() -> list[dict]:
    """Invented records for demonstration only. Clearly marked as example in the UI and report."""
    def r(*a, **k): return new_record(*a, **k)
    D = date
    return [
        r("expense", D(2025, 9, 14), "Seed", 18000, 30, "kg"),
        r("expense", D(2025, 9, 20), "Fertiliser", 42000, 100, "kg", "Agro-dealer", "document"),
        r("expense", D(2025, 10, 2), "Labour", 25000),
        r("harvest", D(2026, 1, 20), "Maize", None, 900, "kg"),
        r("sale", D(2026, 1, 28), "Maize", 207000, 450, "kg", "Cooperative", "document"),
        r("saving", D(2026, 2, 3), "Savings", 50000, evidence="document"),
        r("expense", D(2026, 2, 10), "Seed", 22000, 40, "kg"),
        r("expense", D(2026, 3, 1), "Labour", 30000),
        r("harvest", D(2026, 6, 12), "Beans", None, 400, "kg"),
        r("sale", D(2026, 6, 20), "Beans", 240000, 300, "kg", "Local trader"),
        r("saving", D(2026, 6, 25), "Savings", 60000),
    ]
