"""Smoke test: every page, and every option of every selector, renders without exceptions.
Run from the repo root:  python tests/test_app.py
"""
import logging, sys
from pathlib import Path
from streamlit.testing.v1 import AppTest

logging.disable(logging.WARNING)
ROOT = str(Path(__file__).resolve().parents[1])
PAGES = ["farmer:phone_preview", "farmer:my_records", "landing:home", "lender:lender_view", "about:about"]


def page_script(name, root):
    import sys
    sys.path.insert(0, root)
    from ui import theme, farmer, landing, lender, about
    theme.apply()
    mod, _, fn = name.rpartition(":")
    getattr({"farmer": farmer, "landing": landing, "lender": lender, "about": about}[mod], fn)()


LANG = "rw"


def fresh(name):
    at = AppTest.from_function(page_script, args=(name, ROOT), default_timeout=90)
    at.session_state["lang"] = LANG
    at.session_state["store_ready"] = True           # the browser-storage bridge cannot run in AppTest
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
    from src.i18n import t as _t
    [b for b in at.button if b.label == _t("au.demo", LANG)][0].click().run(); renders += 1   # demo mode
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


def engine_checks():
    from src import records as R
    from src.i18n import t
    recs = R.example_records()
    i = R.insights(recs)
    assert i["span_months"] == 10 and i["sale_months"] == 2 and round(i["net"]) == 310000, i
    assert round(R.instalment(120000, 0, 6)) == 20000 and R.instalment(0, 10, 6) == 0
    assert 52000 < R.instalment(300000, 18, 6) < 53000
    story = R.story(R.EXAMPLE_PROFILE, recs, LANG)
    assert len(story) >= 7 and all(x.strip() for x in story) and R.story({}, [], LANG) == []
    assert not any("{" in x for x in story), "unfilled placeholder in story"
    anon = R.story({}, recs, LANG)
    assert len(anon) == len(story) - 1, "story must omit the farm sentence when the profile is empty"
    for k in ("fx.ok_sale", "fx.ok_expense", "fx.ok_harvest", "fx.ok_saving"):
        assert t(k, LANG, c="x", a="1", q="2")


def add_flow():
    """The tap flow: choose what happened, then save a record through the form."""
    global renders
    at = fresh("farmer:my_records")
    from src.i18n import t as _t
    [b for b in at.button if b.label == _t("au.demo", LANG)][0].click().run()
    at.session_state["records"] = []                           # start the add flow from an empty list
    at.run()
    tiles = {b.key: b for b in at.button if b.key and b.key.startswith("tile_")}
    assert set(tiles) == {"tile_harvest", "tile_sale", "tile_expense", "tile_saving"}, tiles.keys()
    tiles["tile_sale"].click().run(); renders += 1
    assert at.session_state["add_kind"] == "sale" and not at.exception, at.exception
    from src.i18n import t
    nums = [n for n in at.number_input if n.label == t("fr.amount", LANG)]
    nums[0].set_value(50000)
    [b for b in at.button if b.label and t("fx.save", LANG) in b.label][0].click().run(); renders += 1
    assert not at.exception and len(at.session_state["records"]) == 1, (at.exception, at.session_state["records"])
    r = at.session_state["records"][0]
    assert r["kind"] == "sale" and r["amount_rwf"] == 50000 and r["evidence"] == "self", r


def vault_checks():
    import json, time
    from src import vault as V, crypto, records as R
    assert V.normalise_phone("+250 788 123 456") == "0788123456" and V.normalise_phone("788123456") == "0788123456"
    assert V.normalise_phone("0111111111") is None and V.normalise_phone("abc") is None and V.normalise_phone("") is None
    for bad in ("1111", "1234", "4321", "0000", "12", "1234567", "12ab", ""):
        assert V.check_pin(bad, "0781234567"), bad
    assert V.check_pin("4567", "0781234567") and V.check_pin("8260", "0781234567") is None
    phone, pin = "0788123456", "829104"
    prof, recs = dict(R.EXAMPLE_PROFILE), R.example_records()
    blob, key, salt = V.create(phone, pin, prof, recs)
    p2, r2, k2, _ = V.unlock(blob, phone, pin)
    assert r2 == recs and p2["name"] == prof["name"] and k2 == key
    for ph, pn in ((phone, "829105"), ("0788123457", pin)):    # wrong PIN or wrong phone: same generic failure
        try:
            V.unlock(blob, ph, pn); raise AssertionError("opened with wrong credentials")
        except V.VaultError:
            pass
    assert "829104" not in blob and "Example" not in blob and "Maize" not in blob, "plaintext leaked into the vault"
    d = json.loads(blob); d["ct"] = d["ct"][:-4] + ("AAAA" if d["ct"][-4:] != "AAAA" else "BBBB")
    try:
        V.unlock(json.dumps(d), phone, pin); raise AssertionError("tampered vault opened")
    except V.VaultError:
        pass
    b1, b2 = V.reseal(key, salt, phone, prof, recs), V.reseal(key, salt, phone, prof, recs)
    assert json.loads(b1)["nonce"] != json.loads(b2)["nonce"], "nonce reused"
    for junk in ("", "{}", "not json", '{"type":"vault","v":1}', "[]"):
        try:
            V.unlock(junk, phone, pin); raise AssertionError("junk opened")
        except V.VaultError:
            pass
    # a vault cannot be opened as a share and vice versa (purpose is bound into the ciphertext)
    from src import share as S
    pkg, code = S.make_package(prof, recs)
    try:
        V.unlock(pkg, phone, pin); raise AssertionError("share opened as vault")
    except V.VaultError:
        pass
    # lock-out schedule
    assert [V.lock_seconds(n) for n in (1, 4, 5, 6, 7, 20)] == [0, 0, 30, 60, 120, 900]
    lk = None
    for _ in range(5):
        lk = V.register_fail(lk, now=1000.0)
    assert lk["fails"] == 5 and V.wait_left(lk, now=1000.0) == 30 and V.wait_left(lk, now=1031.0) == 0
    assert V.sanitise_lock("garbage") == {"fails": 0, "until": 0.0} and V.sanitise_lock({"fails": 9999, "until": "x"})["fails"] == 0


def share_checks():
    import json
    from datetime import datetime, timedelta, timezone
    from src import share as S, records as R
    prof, recs = dict(R.EXAMPLE_PROFILE, name="Ada"), R.example_records()
    pkg, code = S.make_package(prof, recs, include_names=False, include_farmer_name=False, validity="1d")
    assert len(S.normalise_code(code)) == 12 and set(S.normalise_code(code)) <= set(S.ALPHABET)
    assert "Cooperative" not in pkg and "Ada" not in pkg and "Maize" not in pkg, "plaintext leaked into the share"
    p, r, meta = S.open_package(pkg, code.lower().replace("-", " "))
    assert len(r) == len(recs) and all(x["counterparty"] == "" for x in r), "names must be dropped unless chosen"
    assert p["name"] == "" and meta["names_included"] is False
    pkg2, code2 = S.make_package(prof, recs, include_names=True)
    _, r2, m2 = S.open_package(pkg2, code2)
    assert any(x["counterparty"] for x in r2) and m2["names_included"] is True
    try:
        S.open_package(pkg, "AAAA-AAAA-AAAA"); raise AssertionError("opened with wrong code")
    except S.ShareError as e:
        assert not isinstance(e, S.Expired)
    late = datetime.now(timezone.utc) + timedelta(days=2)
    try:
        S.open_package(pkg, code, now=late); raise AssertionError("expired share opened")
    except S.Expired:
        pass
    d = json.loads(pkg); d["ct"] = d["ct"][:-4] + ("AAAA" if d["ct"][-4:] != "AAAA" else "BBBB")
    try:
        S.open_package(json.dumps(d), code); raise AssertionError("tampered share opened")
    except S.ShareError:
        pass
    # season filter
    seasons = R.seasons_in(recs)
    pk, cd = S.make_package(prof, recs, season=seasons[0])
    _, rr, mm = S.open_package(pk, cd)
    assert 0 < len(rr) < len(recs) and mm["season"] == seasons[0]
    assert S.new_code() != S.new_code()
    try:
        S.make_package(prof, [], validity="7d"); raise AssertionError("empty share allowed")
    except S.ShareError:
        pass


def otp_checks():
    from src import otp as O, usedcodes as U, share as S, records as R
    st_, code = O.issue(None, "0788123456", now=1000)
    assert len(code) == 6 and code.isdigit() and code not in str(st_), "code must not be stored in the clear"
    try:
        O.issue(st_, "0788123456", now=1010); raise AssertionError("resend cooldown not enforced")
    except O.Wait:
        pass
    bad = "000000" if code != "000000" else "111111"
    s2, r = O.verify(st_, bad, now=1020); assert r == "wrong"
    assert O.verify(s2, code, now=2000)[1] == "expired"
    s3, r = O.verify(s2, bad, now=1021); s3, r = O.verify(s3, bad, now=1022); assert r == "locked"
    assert O.verify(s3, code, now=1023)[1] == "locked", "locked state accepted the right code"
    s4, r = O.verify(st_, f"{code[:3]} {code[3:]}", now=1030); assert r == "ok" and s4 is None, "spaces must be ignored"
    st5, code5 = O.issue(st_, "0788123456", now=1100)
    assert O.verify(st5, code, now=1101)[1] in ("wrong", "locked") or code == code5, "old code still works"
    # single-use share codes
    from datetime import datetime, timedelta, timezone
    reg = U.Registry()
    pkg, c = S.make_package(R.EXAMPLE_PROFILE, R.example_records())
    _, _, meta = S.open_package(pkg, c)
    S.claim(reg, meta)
    try:
        S.claim(reg, meta); raise AssertionError("share opened twice")
    except S.Used:
        pass
    pkg2, c2 = S.make_package(R.EXAMPLE_PROFILE, R.example_records())
    S.claim(reg, S.open_package(pkg2, c2)[2])
    try:
        S.claim(reg, {k: v for k, v in meta.items() if k != "id"}); raise AssertionError("id-less share allowed")
    except S.Used:
        pass


def auth_flow():
    """Sign up, add a record, check it is saved encrypted, lock, sign back in, and fail with a wrong PIN."""
    global renders
    from src import vault as V
    from src.i18n import t
    at = fresh("farmer:my_records")
    ti = lambda lbl: [w for w in at.text_input if w.label == t(lbl, LANG)]
    # the sign-up tab comes first when nothing is stored; fill the sign-up form
    ti("au.phone")[0].set_value("0788 123 456")
    [b for b in at.button if b.label == t("otp.send", LANG)][0].click().run(); renders += 1
    assert at.session_state["otp_demo"] and not at.session_state.get("verified_phone")
    ti("otp.code")[0].set_value("000000" if at.session_state["otp_demo"] != "000000" else "111111")
    [b for b in at.button if b.label == t("otp.check", LANG)][0].click().run()
    assert not at.session_state.get("verified_phone"), "wrong code verified the phone"
    ti("otp.code")[0].set_value(at.session_state["otp_demo"])
    [b for b in at.button if b.label == t("otp.check", LANG)][0].click().run(); renders += 1
    assert at.session_state["verified_phone"] == "0788123456", "right code did not verify the phone"
    ti("au.pin")[0].set_value("829104")
    ti("au.pin2")[0].set_value("829104")
    [c for c in at.checkbox if c.label == t("au.ack", LANG)][0].set_value(True)
    [b for b in at.button if b.label == t("au.create", LANG)][0].click().run(); renders += 1
    assert not at.exception, at.exception
    assert at.session_state["auth"]["phone"] == "0788123456", "sign-up did not sign in"
    pend = at.session_state["_pending"]
    assert pend["vault"] and pend["phone"] == "0788123456", "vault was not queued for the browser"
    # add a sale, then the autosave must queue a new vault that contains it
    {b.key: b for b in at.button if b.key}["tile_sale"].click().run()
    [n for n in at.number_input if n.label == t("fr.amount", LANG)][0].set_value(50000)
    [b for b in at.button if b.label and t("fx.save", LANG) in b.label][0].click().run(); renders += 1
    assert len(at.session_state["records"]) == 1 and not at.exception
    at.run()                                                  # the next run persists the change
    blob = at.session_state["_pending"]["vault"]
    _, recs, _, _ = V.unlock(blob, "0788123456", "829104")
    assert len(recs) == 1 and recs[0]["amount_rwf"] == 50000, "autosaved vault is missing the record"
    # lock, then sign in again from what the browser holds
    [b for b in at.button if b.label == t("au.lock", LANG)][0].click().run()
    assert not at.session_state["auth"] if "auth" in at.session_state else True
    assert at.session_state["records"] == [] and "blob" not in at.session_state, "data not cleared on lock"
    at.session_state["_base"] = {"vault": blob, "phone": "0788123456", "lock": "", "ok": True}
    at.session_state["_pending"] = {}
    at.run()
    ti("au.pin")[0].set_value("000000")                       # wrong PIN, five times in a row
    for _ in range(5):
        [b for b in at.button if b.label == t("au.sign_in", LANG)][0].click().run(); renders += 1
        assert not at.session_state.get("auth"), "signed in with a wrong PIN"
    assert V.wait_left(at.session_state["lock"]) > 0, "no lock-out after repeated wrong PINs"
    ti("au.pin")[0].set_value("829104")                       # the right PIN is refused during the wait
    [b for b in at.button if b.label == t("au.sign_in", LANG)][0].click().run()
    assert not at.session_state.get("auth"), "lock-out was bypassed"
    at.session_state["lock"] = {"fails": 0, "until": 0.0}
    at.session_state["_pending"] = {}
    at.run()
    ti("au.pin")[0].set_value("829104")
    [b for b in at.button if b.label == t("au.sign_in", LANG)][0].click().run(); renders += 1
    assert at.session_state["auth"]["phone"] == "0788123456" and len(at.session_state["records"]) == 1


def lender_open_flow():
    """The lender page opens a real share through the form, and escapes hostile text from the file."""
    global renders
    from src import share as S, records as R
    hostile = dict(R.EXAMPLE_PROFILE, name="<img src=x onerror=alert(1)>", crops="<script>x</script>")
    pkg, code = S.make_package(hostile, R.example_records())
    prof, recs, meta = S.open_package(pkg, code)
    at = AppTest.from_function(page_script, args=("lender:lender_view", ROOT), default_timeout=90)
    at.session_state["lang"] = LANG
    at.session_state["lender_records"], at.session_state["lender_profile"] = recs, prof
    at.session_state["lender_meta"] = dict(meta, opened="2026-10-24 10:00", org="<b>Bank</b>")
    at.run(); renders += 1
    assert not at.exception, at.exception
    raw_html = " ".join(m.value for m in at.markdown if m.allow_html)      # only these can inject markup
    assert "<img src=x" not in raw_html and "<script>" not in raw_html and "<b>Bank" not in raw_html, \
        "hostile text reached an HTML element unescaped"
    assert "&lt;img" in raw_html, "farmer name should appear escaped in the farmer card"


def lender_flow():
    """A lender opens a shared file: every period renders; no survey data or score appears anywhere."""
    global renders
    from src import records as R
    shared = R.export_json(R.EXAMPLE_PROFILE, R.example_records())
    prof, recs, _ = R.parse_import(shared)                    # the exact path the uploader uses
    at = AppTest.from_function(page_script, args=("lender:lender_view", ROOT), default_timeout=90)
    at.session_state["lang"] = LANG
    at.session_state["lender_records"], at.session_state["lender_profile"] = recs, prof
    at.run(); renders += 1
    if at.exception:
        failures.append(("lender", "open", [e.value for e in at.exception])); return
    for i, w in enumerate(at.selectbox):
        for opt in w.options:
            at.selectbox[i].select(opt).run(); renders += 1
            if at.exception:
                failures.append(("lender", f"period={opt}", [e.value for e in at.exception]))
    from src.i18n import t
    assert "not verified" in t("ld.disclaimer", "en") and "decision is yours" in t("ld.disclaimer", "en")


def no_dataset_in_product():
    """The product shows no survey statistic and reads no aggregate table."""
    import re
    from ui import landing
    for lg in ("rw", "en"):
        from src import i18n
        i18n.lang = lambda lg=lg: lg
        landing.lang = i18n.lang
        blob = " ".join(landing.props()["s"].values())
        assert not re.search(r"\d+(\.\d+)?\s?%", blob), f"statistic on landing page ({lg})"
    for f in Path(ROOT).glob("ui/*.py"):
        assert "aggregates" not in f.read_text() and "ui.data" not in f.read_text(), f"{f.name} reads survey data"
    assert not (Path(ROOT) / "ui" / "pages.py").exists()


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


for fn in (farmer_flow, add_flow, engine_checks, vault_checks, share_checks, otp_checks, auth_flow, lender_flow, lender_open_flow, ussd_flow, i18n_complete):
    for LANG in ("rw", "en"):
        try:
            fn()
        except Exception as e:
            import traceback
            failures.append((fn.__name__, LANG, [repr(e), traceback.format_exc().splitlines()[-6:]]))

try:
    no_dataset_in_product()
except Exception as e:
    failures.append(("no_dataset_in_product", "-", [repr(e)]))

print(f"{renders} renders, {len(failures)} failures")
for f in failures[:10]:
    print("FAIL", f)
sys.exit(1 if failures else 0)
