"""The farmer's PIN-locked profile ("vault"). Channel-agnostic and free of any UI.

A vault is one JSON string holding the farmer's profile and records, encrypted with a key derived from
phone number + PIN. It lives in the farmer's own browser storage and can be saved as a backup file. The server
keeps nothing: only the unlocked data and key live in the session memory while the farmer is signed in.

Honest limits (see docs/security.md): the phone number is a label and is not verified (no SMS); a 4-6 digit PIN
can be guessed offline by someone who copies the vault, so the key derivation is deliberately slow and the app
asks for a PIN that is not trivial. Lock-out slows guessing inside the app only.
"""
from __future__ import annotations
import json
import re
import time

from src import crypto

VERSION = 1
MAX_FAILS_FREE = 4          # the 5th wrong try starts a lock-out
MAX_LOCK_S = 15 * 60
IDLE_LOCK_S = 15 * 60


class VaultError(Exception):
    """Wrong phone number or PIN, or a damaged vault. Never says which."""


def normalise_phone(raw: str) -> str | None:
    """Rwandan mobile in any common form -> '07XXXXXXXX', else None."""
    s = re.sub(r"[\s\-().]", "", raw or "")
    s = re.sub(r"^(\+?250)", "0", s)
    if re.fullmatch(r"7[2389]\d{7}", s):
        s = "0" + s
    return s if re.fullmatch(r"07[2389]\d{7}", s) else None


def mask_phone(phone: str) -> str:
    return f"{phone[:3]}••• ••{phone[-3:]}" if phone else ""


def check_pin(pin: str, phone: str = "") -> str | None:
    """Return an i18n key if the PIN is unacceptable, else None. 4-6 digits, not trivially guessable."""
    if not re.fullmatch(r"\d{4,6}", pin or ""):
        return "au.pin_format"
    digits = [int(c) for c in pin]
    if len(set(pin)) == 1:
        return "au.pin_trivial"
    steps = {b - a for a, b in zip(digits, digits[1:])}
    if steps in ({1}, {-1}):
        return "au.pin_trivial"
    if phone and pin in phone[-len(pin):]:
        return "au.pin_phone"
    return None


def _aad(phone: str) -> bytes:
    return f"finbridge-vault-v{VERSION}|{phone}".encode()


def _pack(salt: bytes, nonce: bytes, ct: bytes) -> str:
    return json.dumps({"app": "FinBridge", "type": "vault", "v": VERSION, "kdf": "scrypt",
                       "n": crypto.KDF_N, "salt": crypto.b64e(salt), "nonce": crypto.b64e(nonce),
                       "ct": crypto.b64e(ct)}, separators=(",", ":"))


def create(phone: str, pin: str, profile: dict, records: list[dict]) -> tuple[str, bytes, bytes]:
    """New vault. Returns (blob, key, salt); keep key and salt in the session to save again without the PIN."""
    salt = crypto.new_salt()
    key = crypto.derive_key(f"{pin}|{phone}", salt)
    return reseal(key, salt, phone, profile, records), key, salt


def reseal(key: bytes, salt: bytes, phone: str, profile: dict, records: list[dict]) -> str:
    """Encrypt the current data again with a fresh nonce (cheap: no key derivation)."""
    payload = json.dumps({"profile": profile, "records": records, "saved": int(time.time())},
                         ensure_ascii=False).encode("utf-8")
    nonce, ct = crypto.seal(key, payload, _aad(phone))
    return _pack(salt, nonce, ct)


def unlock(blob: str, phone: str, pin: str) -> tuple[dict, list[dict], bytes, bytes]:
    """Open a vault. Returns (profile, records, key, salt). Raises VaultError for any failure."""
    try:
        d = json.loads(blob)
        if d.get("type") != "vault" or d.get("v") != VERSION or d.get("n") != crypto.KDF_N:
            raise ValueError
        salt = crypto.b64d(d["salt"])
        key = crypto.derive_key(f"{pin}|{phone}", salt)
        raw = crypto.unseal(key, crypto.b64d(d["nonce"]), crypto.b64d(d["ct"]), _aad(phone))
        data = json.loads(raw)
    except Exception as e:
        raise VaultError("cannot open") from e
    # untrusted even after decrypting: re-validate like any import
    from src import records as R
    prof, recs, _ = R.parse_import(json.dumps({"profile": data.get("profile", {}), "records": data.get("records", [])}))
    return prof, recs, key, salt


# ---------------------------------------------------------------- lock-out
def lock_seconds(fails: int) -> int:
    """Wait after this many wrong tries in a row: none for the first four, then 30 s doubling up to 15 min."""
    if fails <= MAX_FAILS_FREE:
        return 0
    return min(MAX_LOCK_S, 30 * 2 ** (fails - MAX_FAILS_FREE - 1))


def wait_left(lock: dict | None, now: float | None = None) -> int:
    now = time.time() if now is None else now
    return max(0, int((lock or {}).get("until", 0) - now + 0.999))


def register_fail(lock: dict | None, now: float | None = None) -> dict:
    now = time.time() if now is None else now
    fails = int((lock or {}).get("fails", 0)) + 1
    return {"fails": fails, "until": now + lock_seconds(fails)}


def sanitise_lock(raw) -> dict:
    """The lock record comes from browser storage, so treat it as untrusted."""
    try:
        return {"fails": max(0, min(int(raw["fails"]), 50)), "until": max(0.0, float(raw["until"]))}
    except Exception:
        return {"fails": 0, "until": 0.0}
