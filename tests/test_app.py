"""Smoke test: every page, and every option of every selector, renders without exceptions.
Run from the repo root:  python tests/test_app.py
"""
import logging, sys
from pathlib import Path
from streamlit.testing.v1 import AppTest

logging.disable(logging.WARNING)
ROOT = str(Path(__file__).resolve().parents[1])
PAGES = ["overview", "who", "why", "farmers", "districts", "recommendations", "methods",
         "farmer:why_records", "farmer:adjusted", "farmer:phone_preview", "farmer:my_records"]


def page_script(name, root):
    import sys
    sys.path.insert(0, root)
    from ui import theme, pages, farmer
    theme.apply()
    mod, _, fn = name.rpartition(":")
    getattr(farmer if mod else pages, fn)()


LANG = "rw"


def fresh(name):
    at = AppTest.from_function(page_script, args=(name, ROOT), default_timeout=90)
    at.session_state["lang"] = LANG
    return at.run()


failures, renders = [], 0


def sweep():
    """Every page, and every option of every selector, in the current LANG."""
    global renders
    for name in PAGES:
        at = fresh(name); renders += 1
        if at.exception:
            failures.append((f"{LANG}:{name}", "initial", [e.value for e in at.exception])); continue
        for kind in ("selectbox", "radio"):
            for i, w in enumerate(getattr(at, kind)):
                for j in range(len(w.options)):
                    at2 = fresh(name)
                    if kind == "selectbox":
                        at2.selectbox[i].select_index(j).run()
                    else:
                        at2.radio[i].set_value(at2.radio[i].options[j]).run()
                    renders += 1
                    if at2.exception:
                        failures.append((f"{LANG}:{name}", f"{kind}{i}[{j}]={w.options[j]}",
                                         [e.value for e in at2.exception]))


for LANG in ("rw", "en"):
    sweep()

# ---- stateful farmer flows -------------------------------------------------
def farmer_flow():
    global renders
    at = fresh("farmer:my_records")
    at.button[0].click().run(); renders += 1                  # "Try with example records"
    if at.exception:
        failures.append(("my_records", "example", [e.value for e in at.exception])); return
    assert len(at.session_state["records"]) == 11, "example records not loaded"
    for i in range(len(at.selectbox)):                        # every period in summary and report
        w = at.selectbox[i]
        if w.label in ("Period", "Igihe"):
            for opt in w.options:
                at.selectbox[i].select(opt).run(); renders += 1
                if at.exception:
                    failures.append(("my_records", f"period={opt}", [e.value for e in at.exception]))
    # the web form saves a record
    from src import records as R
    html = R.report_html(R.EXAMPLE_PROFILE, R.example_records(), None, True)
    assert "EXAMPLE DATA" in html and "does not score farmers" in html, "report disclaimers missing"
    assert "ntiha abahinzi amanota" in R.report_html(R.EXAMPLE_PROFILE, R.example_records(), None, True, "rw")
    x = R.report_html({"name": "<script>alert(1)</script>"}, R.example_records(), None)
    assert "<script>alert" not in x, "report does not escape user text"
    # import must never grant 'confirmed' evidence and must skip junk
    bad = '{"records":[{"date":"2026-01-01","kind":"sale","item":"Maize","amount_rwf":5000,"evidence":"confirmed"},' \
          '{"date":"nope","kind":"sale","item":"x","amount_rwf":1},{"date":"2026-01-01","kind":"sale","item":"x","amount_rwf":-5}]}'
    prof, recs, skipped = R.parse_import(bad)
    assert len(recs) == 1 and recs[0]["evidence"] == "document" and skipped == 2, "import validation failed"


def ussd_flow():
    from src import ussd as U, records as R
    st_, recs = {}, []
    for t in ["1", "1", "50000", "30", "2", "3", "12000", "4", "20000", "3", "2", "400", "5", "0", "x", "9", "1", "9",
              "1", "1", "abc", "1", "1", "5", "abc", "2", "1", "-5"]:
        scr, st_, end = U.step(st_, t, recs, lg=LANG)
        assert len(scr) <= 160, f"USSD screen over 160 chars ({LANG}): {len(scr)}"
        if end: st_ = {}
    st_, recs = {}, []
    for t in ["1", "1", "50000", "30", "2", "3", "12000", "4", "20000", "3", "2", "400", "5"]:
        scr, st_, end = U.step(st_, t, recs, lg=LANG)
    s = R.summarise(recs)
    assert (s["sales"], s["expenses"], s["saved"]) == (50000, 12000, 20000) and s["harvest_kg"] == {"Beans": 400}, s
    scr, st_, _ = U.step({}, "9", recs, lg=LANG)
    assert scr.startswith("Choose" if LANG == "en" else "Hitamo"), "bad menu input must re-prompt"
    scr, st_, _ = U.step({"stage": "amount", "kind": "sale", "item": "Maize"}, "abc", recs, lg=LANG)
    assert ("number" if LANG == "en" else "umubare") in scr, "non-numeric amount must re-prompt"


def i18n_complete():
    import re
    from src.i18n import STR, t
    fmt = lambda x: set(re.findall(r"{(\w+)}", x))
    for k, (rw, en) in STR.items():
        assert rw.strip(), f"missing Kinyarwanda: {k}"
        if not k.startswith("sum."):
            assert en.strip(), f"missing English: {k}"
            assert fmt(rw) == fmt(en), f"placeholder mismatch in {k}: {fmt(rw)} vs {fmt(en)}"
    from src import records as R
    for lg in ("rw", "en"):
        h = R.report_html(R.EXAMPLE_PROFILE, R.example_records(), None, True, lg)
        assert f'lang="{lg}"' in h and (t("rp.title", lg) in h), f"report not in {lg}"
    assert "Incamake" in R.report_html({}, [], None, False, "rw")
    for k in R.KINDS: assert f"kind.{k}" in STR
    for it_ in R.CROPS + R.EXPENSES + ["Savings"]: assert f"item.{it_}" in STR, it_
    for u in R.UNITS: assert f"unit.{u}" in STR
    for e_ in R.EVIDENCE: assert f"ev.{e_}" in STR
    msgs = ["v.date", "v.kind", "v.ev", "v.amount", "v.harvest", "v.big_amount", "v.big_qty", "v.item"]
    assert all(m in STR for m in msgs)


for fn in (farmer_flow, ussd_flow, i18n_complete):
    for LANG in ("rw", "en"):
        try:
            fn()
        except Exception as e:
            failures.append((fn.__name__, LANG, [repr(e)]))

print(f"{renders} renders, {len(failures)} failures")
for f in failures[:10]:
    print("FAIL", f)
sys.exit(1 if failures else 0)
