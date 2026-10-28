"""Farmer sign-in: a PIN-locked profile kept in the farmer's own browser, never on our server.

Flow: create profile (phone + PIN) -> records are encrypted (src/vault.py) and written to the browser's
local storage through a tiny JavaScript bridge -> next visit, phone + PIN unlock them. A locked backup file can
restore the profile on another phone. The server keeps the unlocked data and key in session memory only while
the farmer is signed in, and drops them on lock, sign-out or after 15 minutes of inactivity.
"""
from __future__ import annotations
import hashlib
import json
import time
import uuid

import streamlit as st

from src import otp as O
from src import records as R
from src import vault as V
from src.i18n import t

# The bridge only copies opaque strings between Python and localStorage. It never sees a PIN or a record.
_JS = """
export default function(component) {
  const { data, setStateValue, parentElement } = component;
  const KEYS = { vault: 'finbridge.vault.v1', phone: 'finbridge.phone.v1', lock: 'finbridge.lock.v1' };
  const out = {};
  let ok = true;
  try {
    if (data && data.token && window.__fbToken !== data.token) {
      window.__fbToken = data.token;
      for (const name of Object.keys(KEYS)) {
        const v = data[name];
        if (typeof v !== 'string') continue;
        if (v === '') localStorage.removeItem(KEYS[name]); else localStorage.setItem(KEYS[name], v);
      }
    }
    for (const name of Object.keys(KEYS)) out[name] = localStorage.getItem(KEYS[name]) || '';
  } catch (e) {
    ok = false;
    for (const name of Object.keys(KEYS)) out[name] = '';
  }
  out.ok = ok;
  const sig = JSON.stringify(out);
  if (data && data.write_only) return;           // writers never report back: a rerun would wipe on-screen messages
  if (parentElement.__fbSig !== sig) { parentElement.__fbSig = sig; setStateValue('store', sig); }
}
"""
_bridge = None


def _mount(key: str, data: dict, report: bool = True):
    """Mount the storage bridge. Registered on first use, and again if the runtime has lost the registration.
    report=False makes a write-only instance: it has no callback, so it can never trigger a rerun."""
    global _bridge
    kw = {"on_store_change": (lambda: None)} if report else {}
    if _bridge is None:
        _bridge = st.components.v2.component("finbridge_store", js=_JS)
    try:
        return _bridge(key=key, data=data, **kw)
    except st.errors.StreamlitAPIException:
        _bridge = st.components.v2.component("finbridge_store", js=_JS)
        return _bridge(key=key, data=data, **kw)
_EMPTY = {"vault": "", "phone": "", "lock": "", "ok": True}
_RESET_LOCK = json.dumps({"fails": 0, "until": 0})


# ---------------------------------------------------------------- browser storage
def _write(**kw):
    ss = st.session_state
    ss["_pending"] = {**ss.get("_pending", {}), **kw, "token": uuid.uuid4().hex}


def store() -> dict | None:
    """What the browser holds (with our own latest writes on top), or None until the browser has reported."""
    ss = st.session_state
    res = _mount("fb_read", {})
    raw = getattr(res, "store", None)
    if raw:
        ss["store_ready"] = True
        try:
            base = {**_EMPTY, **json.loads(raw)}
        except Exception:
            base = dict(_EMPTY)
        ss["_base"] = base
    if not ss.get("store_ready"):
        return None
    pend = {k: v for k, v in ss.get("_pending", {}).items() if k != "token"}
    return {**ss.get("_base", _EMPTY), **pend}


def flush():
    """Call once at the end of every run: hands any pending write to the browser."""
    p = st.session_state.get("_pending")
    if p:
        _mount(f"fb_write_{p['token']}", {**p, "write_only": True}, report=False)   # new key per save: mounts afresh


# ---------------------------------------------------------------- session state
def signed_in() -> bool:
    return bool(st.session_state.get("auth"))


def in_demo() -> bool:
    return bool(st.session_state.get("demo"))


def _hash(ss) -> str:
    return hashlib.sha256(json.dumps([ss.profile, ss.records], sort_keys=True, default=str).encode()).hexdigest()


def persist():
    """Encrypt and save whenever the profile or records changed. Cheap: no key derivation, a fresh nonce."""
    ss = st.session_state
    a = ss.get("auth")
    if not a:
        return
    h = _hash(ss)
    if h != ss.get("_hash"):
        blob = V.reseal(a["key"], a["salt"], a["phone"], ss.profile, ss.records)
        ss["_hash"], ss["blob"] = h, blob
        _write(vault=blob)


def lock_session():
    """Forget the unlocked data and key. The encrypted copy stays safe in the browser."""
    ss = st.session_state
    for k in ("auth", "blob", "_hash", "demo", "last_share", "verified_phone", "otp", "otp_demo"):
        ss.pop(k, None)
    ss.records, ss.example = [], False
    ss.profile = dict(name="", district="", crops="", farm_ha=0.0)
    ss.pop("add_kind", None)


def _start(phone, prof, recs, key, salt):
    ss = st.session_state
    ss.profile, ss.records, ss.example = prof, recs, False
    ss["auth"] = {"phone": phone, "key": key, "salt": salt}
    ss["_hash"] = _hash(ss)
    ss["last_active"] = time.time()
    ss.lock = {"fails": 0, "until": 0.0}
    _write(phone=phone, lock=_RESET_LOCK)
    st.rerun()


def _lock_state(stored) -> dict:
    ss = st.session_state
    a, b = V.sanitise_lock(_load_json(stored.get("lock"))), ss.get("lock") or {"fails": 0, "until": 0.0}
    return a if a["fails"] >= b["fails"] else b


def _load_json(raw):
    try:
        return json.loads(raw) if raw else {}
    except Exception:
        return {}


def _wait_msg(lock) -> bool:
    left = V.wait_left(lock)
    if left:
        st.warning(t("au.wait", s=left))
    return bool(left)


def _failed(lock):
    ss = st.session_state
    lock = V.register_fail(lock)
    ss.lock = lock
    _write(lock=json.dumps(lock))
    st.error(t("au.fail"))
    left = V.MAX_FAILS_FREE + 1 - lock["fails"]
    if left > 0:
        st.caption(t("au.tries", n=left))
    elif lock["until"] > time.time():
        st.warning(t("au.wait", s=V.wait_left(lock)))


# ---------------------------------------------------------------- screens
def _sign_in_form(stored):
    ss = st.session_state
    saved_phone = stored.get("phone", "")
    use_saved = bool(saved_phone) and not ss.get("other_number")
    with st.form("signin"):
        if use_saved:
            st.markdown(f"**{t('au.welcome_back', p=V.mask_phone(saved_phone))}**")
            phone_raw = saved_phone
        else:
            phone_raw = st.text_input(t("au.phone"), max_chars=20, autocomplete="tel")
        pin = st.text_input(t("au.pin"), type="password", max_chars=6, autocomplete="current-password")
        go = st.form_submit_button(t("au.sign_in"), type="primary", width="stretch")
    if use_saved and st.button(t("au.not_you")):
        ss["other_number"] = True
        st.rerun()
    if go:
        lock = _lock_state(stored)
        if _wait_msg(lock):
            return
        phone = V.normalise_phone(phone_raw)
        if not phone or not stored.get("vault"):
            _failed(lock)
            return
        try:
            prof, recs, key, salt = V.unlock(stored["vault"], phone, pin)
        except V.VaultError:
            _failed(lock)
            return
        _start(phone, prof, recs, key, salt)


def _verify_phone() -> str | None:
    """Step 1 of sign-up: a one-time code proves the farmer holds the phone. Returns the verified number or None."""
    ss = st.session_state
    if ss.get("verified_phone"):
        st.success(t("otp.verified", p=V.mask_phone(ss["verified_phone"])))
        if st.button(t("otp.change")):
            for k in ("verified_phone", "otp", "otp_demo"):
                ss.pop(k, None)
            st.rerun()
        return ss["verified_phone"]
    with st.form("otp_send"):
        phone_raw = st.text_input(t("au.phone"), max_chars=20, autocomplete="tel")
        send = st.form_submit_button(t("otp.send"), type="primary", width="stretch")
    if send:
        phone = V.normalise_phone(phone_raw)
        if not phone:
            st.error(t("au.phone_bad"))
        else:
            try:
                ss.otp, code = O.issue(ss.get("otp"), phone)
            except O.Wait as w:
                st.warning(t("otp.wait", s=w.seconds))
            else:
                ss.otp_demo = None if O.send_sms(phone, t("otp.sms", c=code)) else code
    if ss.get("otp"):
        if ss.get("otp_demo"):
            st.info(t("otp.demo_sms", c=ss.otp_demo))
        else:
            st.caption(t("otp.sent", p=V.mask_phone(ss.otp["phone"])))
        with st.form("otp_check"):
            code = st.text_input(t("otp.code"), max_chars=8, autocomplete="one-time-code")
            ok = st.form_submit_button(t("otp.check"), width="stretch")
        if ok:
            phone = ss.otp["phone"]
            ss.otp, res = O.verify(ss.otp, code)
            if res == "ok":
                ss["verified_phone"] = phone
                ss.pop("otp_demo", None)
                st.rerun()
            st.error(t(f"otp.{res}"))
    return None


def _sign_up_form(stored):
    phone_ok = _verify_phone()
    if not phone_ok:
        st.caption(t("au.why"))
        return
    with st.form("signup"):
        phone_raw = phone_ok
        name = st.text_input(t("au.name"), max_chars=60)
        pin = st.text_input(t("au.pin"), type="password", max_chars=6, autocomplete="new-password")
        pin2 = st.text_input(t("au.pin2"), type="password", max_chars=6, autocomplete="new-password")
        replace = False
        if stored.get("vault"):
            st.warning(t("au.exists"))
            replace = st.checkbox(t("au.replace"))
        ack = st.checkbox(t("au.ack"))
        go = st.form_submit_button(t("au.create"), type="primary", width="stretch")
    st.caption(t("au.why"))
    if not go:
        return
    phone = V.normalise_phone(phone_raw)
    err = (None if phone else "au.phone_bad") or V.check_pin(pin, phone or "") or \
          (None if pin == pin2 else "au.pin_mismatch")
    if err:
        st.error(t(err))
    elif stored.get("vault") and not replace:
        st.error(t("au.exists"))
    elif not ack:
        st.error(t("au.ack"))
    else:
        prof = dict(name=name.strip(), district="", crops="", farm_ha=0.0)
        blob, key, salt = V.create(phone, pin, prof, [])
        st.session_state["blob"] = blob
        _write(vault=blob)
        _start(phone, prof, [], key, salt)


def _restore_form(stored):
    with st.form("restore"):
        up = st.file_uploader(t("au.restore_file"), type=["fbvault", "json"])
        phone_raw = st.text_input(t("au.phone"), max_chars=20, autocomplete="tel", key="rs_phone")
        pin = st.text_input(t("au.pin"), type="password", max_chars=6, key="rs_pin")
        go = st.form_submit_button(t("au.restore"), type="primary", width="stretch")
    if not go:
        return
    lock = _lock_state(stored)
    if _wait_msg(lock):
        return
    phone = V.normalise_phone(phone_raw)
    try:
        if not (up and phone):
            raise V.VaultError
        blob = up.getvalue().decode("utf-8")
        prof, recs, key, salt = V.unlock(blob, phone, pin)
    except Exception:
        st.error(t("au.restore_bad"))
        _failed(lock)
        return
    st.session_state["blob"] = blob
    _write(vault=blob)
    _start(phone, prof, recs, key, salt)


def _forgot(stored):
    with st.expander(t("au.forgot")):
        st.markdown(t("au.forgot_b"))
        if stored.get("vault"):
            sure = st.checkbox(t("au.erase_ack"), key="erase_ack")
            if st.button(t("au.erase"), disabled=not sure):
                _write(vault="", phone="", lock=_RESET_LOCK)
                st.session_state.lock = {"fails": 0, "until": 0.0}
                st.session_state.pop("other_number", None)
                st.success(t("au.erased"))
                st.rerun()


def _start_demo():
    ss = st.session_state
    ss.records, ss.profile, ss.example = R.example_records(), dict(R.EXAMPLE_PROFILE_WITH_PLAN), True
    ss["demo"] = True
    ss["last_active"] = time.time()
    st.rerun()


def gate() -> bool:
    """True when the farmer may see their records (signed in, or in the demo). Otherwise shows the sign-in screen."""
    ss = st.session_state
    now = time.time()
    if (signed_in() or in_demo()) and now - ss.get("last_active", now) > V.IDLE_LOCK_S:
        lock_session()
        ss["_idle"] = True
    if signed_in() or in_demo():
        ss["last_active"] = now
        return True
    stored = store()
    if stored is None:
        st.caption(t("au.loading"))
        if st.button(t("au.skip_loading")):
            ss["store_ready"] = True
            st.rerun()
        return False
    if ss.pop("_idle", False):
        st.info(t("au.idle"))
    if not stored.get("ok", True):
        st.warning(t("au.nostore"))
    st.markdown(f"### {t('au.title')}")
    labels = [t("au.tab_in"), t("au.tab_new"), t("au.tab_restore")]
    order = labels if stored.get("vault") else [labels[1], labels[0], labels[2]]
    for label, tab in zip(order, st.tabs(order, default=order[0])):
        with tab:
            {labels[0]: _sign_in_form, labels[1]: _sign_up_form, labels[2]: _restore_form}[label](stored)
    _forgot(stored)
    st.divider()
    st.caption(t("au.demo_note"))
    if st.button(t("au.demo"), width="stretch"):
        _start_demo()
    return False


def account_bar():
    ss = st.session_state
    c1, c2 = st.columns([4, 1])
    if in_demo():
        c1.info(t("au.demo_bar"))
        if c2.button(t("au.leave_demo"), width="stretch"):
            lock_session()
            st.rerun()
    else:
        c1.markdown(f"🔒 {t('au.bar', p=V.mask_phone(ss.auth['phone']))}")
        if c2.button(t("au.lock"), width="stretch"):
            lock_session()
            st.rerun()
