"""Loan purpose sheet: a farmer's plain statement of what a loan would be for and how it would be repaid.

Channel-agnostic, no UI. Answers the most cited refusal reason in AHS ("unclear purpose") with a clear plan, without
claiming it improves approval. Everything is self-reported; nothing here scores or recommends.
Stored in the profile under "loan_plan", so it travels with the encrypted vault and the JSON backup, and goes to a
lender only when the farmer ticks "include my loan plan" when sharing.
"""
from __future__ import annotations
import html
from datetime import date

PURPOSES = ["inputs", "equipment", "livestock", "other"]
REPAY = ["crop_sales", "other_income"]
GROUPS = ["tontine", "cooperative", "twigire"]
MAX_ITEMS = 8
EMPTY = dict(purpose="", purpose_other="", items=[], cost_rwf=None, plant_month=None, harvest_month=None,
             repay=[], groups=[])


def _month(v):
    try:
        m = int(v)
    except (TypeError, ValueError):
        return None
    return m if 1 <= m <= 12 else None


def sanitize(x) -> dict | None:
    """Keep only known fields and types (the input may come from an untrusted file). None if there is no usable plan."""
    if not isinstance(x, dict) or x.get("purpose") not in PURPOSES:
        return None
    items = []
    for it in (x.get("items") or [])[:MAX_ITEMS]:
        if not isinstance(it, dict) or not str(it.get("item", "")).strip():
            continue
        try:
            q = float(it.get("qty")) if it.get("qty") not in (None, "") else None
        except (TypeError, ValueError):
            q = None
        items.append(dict(item=str(it["item"]).strip()[:40], qty=q if q is not None and 0 <= q <= 1e8 else None,
                          unit=str(it.get("unit", "")).strip()[:12]))
    try:
        cost = None if x.get("cost_rwf") in (None, "") else float(x["cost_rwf"])
    except (TypeError, ValueError):
        cost = None
    if cost is not None and not 0 <= cost <= 1e10:
        cost = None
    return dict(purpose=x["purpose"], purpose_other=str(x.get("purpose_other", "")).strip()[:40], items=items,
                cost_rwf=cost, plant_month=_month(x.get("plant_month")), harvest_month=_month(x.get("harvest_month")),
                repay=[r for r in REPAY if r in (x.get("repay") or [])],
                groups=[g for g in GROUPS if g in (x.get("groups") or [])])


def validate(plan: dict) -> str | None:
    """An i18n key if the plan is not usable, else None."""
    if plan.get("purpose") not in PURPOSES:
        return "lp.v_purpose"
    if plan["purpose"] == "other" and not plan.get("purpose_other", "").strip():
        return "lp.v_other"
    if not (plan.get("cost_rwf") or 0) > 0:
        return "lp.v_cost"
    return None


def plan_html(profile: dict, plan: dict, lg: str = "en", example: bool = False) -> str:
    """One printable page. Escapes all user text."""
    from src.i18n import t
    T_ = lambda k, **kw: t(k, lg, **kw)
    e = html.escape
    ng = T_("rp.none")
    mon = lambda m: T_(f"lp.m{m}") if m else ng
    cur = T_("rwf")
    purpose = T_(f"lp.p_{plan['purpose']}") + (f": {e(plan['purpose_other'])}" if plan.get("purpose_other") else "")
    qty = lambda i: "" if i["qty"] is None else f"{i['qty']:g}"
    rows = "".join(f"<tr><td>{e(i['item'])}</td><td>{qty(i)} {e(i['unit'])}</td></tr>"
                   for i in plan["items"]) or f"<tr><td colspan=2>{ng}</td></tr>"
    cost = ng if plan.get("cost_rwf") is None else f"{plan['cost_rwf']:,.0f} {cur}"
    join = lambda keys, pre: ", ".join(T_(f"{pre}{k}") for k in keys) or ng
    banner = (f'<p style="background:#C2922A;color:#fff;padding:8px"><b>{T_("rp.example")}</b></p>' if example else "")
    return f"""<!doctype html><html lang="{lg}"><meta charset="utf-8"><title>{T_('lp.title')}</title>
<body style="font-family:Atkinson Hyperlegible,Segoe UI,sans-serif;max-width:720px;margin:2rem auto;color:#1C2B24">
{banner}<h1>{T_('lp.title')}</h1>
<p>{T_('rp.farmer')}: <b>{e(profile.get('name') or ng)}</b> · {T_('rp.district')}: {e(profile.get('district') or ng)}
 · {T_('rp.size')}: {profile.get('farm_ha', 0):g} ha · {T_('rp.crops')}: {e(profile.get('crops') or ng)}</p>
<p>{T_('rp.generated')} {date.today().isoformat()}</p>
<div style="border-left:4px solid #8E3B2E;padding:6px 12px;background:#EEF2EC">{T_('lp.note')}</div>
<h2>{T_('lp.what')}</h2><p><b>{purpose}</b></p>
<h2>{T_('lp.items')}</h2><table cellpadding=6>{rows}</table>
<p>{T_('lp.cost')}: <b>{cost}</b></p>
<h2>{T_('lp.when')}</h2>
<p>{T_('lp.plant')}: <b>{mon(plan.get('plant_month'))}</b> · {T_('lp.harvest')}: <b>{mon(plan.get('harvest_month'))}</b></p>
<h2>{T_('lp.repay')}</h2><p><b>{join(plan['repay'], 'lp.r_')}</b></p>
<h2>{T_('lp.groups')}</h2><p><b>{join(plan['groups'], 'lp.g_')}</b></p>
<p style="font-size:.85rem">{T_('lp.footer')}</p>
</body></html>"""


EXAMPLE_PLAN = dict(purpose="inputs", purpose_other="", cost_rwf=95000, plant_month=9, harvest_month=1,
                    items=[dict(item="Maize seed", qty=30, unit="kg"), dict(item="DAP and urea (as advised)", qty=100, unit="kg")],
                    repay=["crop_sales"], groups=["tontine", "cooperative"])
