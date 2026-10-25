"""One-time phone codes (SMS OTP). Channel-agnostic and free of any UI.

Used to prove a farmer controls the phone number when a profile is created. The code is 6 digits, valid for
5 minutes, allows 3 wrong tries, and a new one cannot be requested for 30 seconds. Only a salted HMAC of the code
is kept in the state dict, never the code itself.

DEMO MODE: no SMS gateway is connected yet, so send_sms() returns False and the screen shows the code in a clearly
labelled demo box. To go live, make send_sms() call a provider (e.g. Africa's Talking) and return True; nothing
else changes, and the UI then stops showing the code.
"""
from __future__ import annotations
import hashlib
import hmac
import secrets
import time

DIGITS = 6
TTL_S = 300
MAX_TRIES = 3
RESEND_S = 30


class Wait(Exception):
    """A new code was requested too soon."""
    def __init__(self, seconds: int):
        super().__init__(seconds)
        self.seconds = seconds


def _mac(salt: bytes, phone: str, code: str) -> str:
    return hmac.new(salt, f"{phone}|{code}".encode(), hashlib.sha256).hexdigest()


def issue(state: dict | None, phone: str, now: float | None = None) -> tuple[dict, str]:
    """New code for this phone. Returns (new_state, code). Raises Wait inside the resend cooldown."""
    now = time.time() if now is None else now
    if state and now - state.get("sent", 0) < RESEND_S:
        raise Wait(int(RESEND_S - (now - state["sent"]) + 0.999))
    code = "".join(secrets.choice("0123456789") for _ in range(DIGITS))
    salt = secrets.token_bytes(16)
    return {"phone": phone, "salt": salt, "mac": _mac(salt, phone, code), "exp": now + TTL_S, "tries": 0,
            "sent": now}, code


def verify(state: dict | None, code: str, now: float | None = None) -> tuple[dict | None, str]:
    """Returns (new_state, result), result in ok | wrong | expired | locked. A good code is used up."""
    now = time.time() if now is None else now
    if not state:
        return state, "expired"
    if now > state["exp"]:
        return None, "expired"
    if state["tries"] >= MAX_TRIES:
        return state, "locked"
    digits = "".join(c for c in (code or "") if c.isdigit())
    if len(digits) == DIGITS and hmac.compare_digest(state["mac"], _mac(state["salt"], state["phone"], digits)):
        return None, "ok"
    state = dict(state, tries=state["tries"] + 1)
    return state, ("locked" if state["tries"] >= MAX_TRIES else "wrong")


def send_sms(phone: str, text: str) -> bool:
    """Deliver an SMS. Demo build: nothing is sent, so return False and let the UI show the code."""
    return False
