"""Consent-based sharing: the farmer packages chosen records into an encrypted file and gives the lender a
single-use code separately (see usedcodes.py). No server is involved. Channel-agnostic and free of any UI.

What the farmer controls: which period, whether buyer/seller names are included, whether their name is
included, and how long the share stays valid. What we cannot promise: a lender who has opened a share can keep
what they saw (as with a printed report). Expiry is enforced by FinBridge when opening, not by the file itself.
"""
from __future__ import annotations
import json
import re
import secrets
from datetime import datetime, timedelta, timezone

from src import crypto
from src import records as R

VERSION = 1
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"      # no 0/O/1/I/L: easy to read aloud and copy
CODE_LEN = 12                                       # 31^12, about 59 bits
VALIDITY_HOURS = {"1d": 24, "7d": 24 * 7, "30d": 24 * 30}


class ShareError(Exception):
    """Wrong code, damaged file or expired share. Wrong code and damage are not told apart."""


class Expired(ShareError):
    pass


class Used(ShareError):
    """The code was already used to open this share. A share opens once."""


def new_code() -> str:
    raw = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LEN))
    return "-".join(raw[i:i + 4] for i in range(0, CODE_LEN, 4))


def normalise_code(code: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (code or "").upper())


def _aad() -> bytes:
    return f"finbridge-share-v{VERSION}".encode()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def make_package(profile: dict, records: list[dict], *, season: str | None = None, include_names: bool = False,
                 include_farmer_name: bool = True, validity: str = "7d") -> tuple[str, str]:
    """Returns (package_json, code). Only the chosen data goes in; the code is never stored anywhere."""
    from datetime import date
    recs = [r for r in records if season is None or R.season_of(date.fromisoformat(r["date"])) == season]
    if not recs:
        raise ShareError("nothing to share")
    recs = [dict(r, counterparty=r["counterparty"] if include_names else "") for r in recs]
    prof = dict(profile)
    if not include_farmer_name:
        prof["name"] = ""
    created = _now()
    expires = created + timedelta(hours=VALIDITY_HOURS[validity])
    code = new_code()
    meta = {"id": secrets.token_hex(8), "created": created.isoformat(timespec="seconds"), "expires": expires.isoformat(timespec="seconds"),
            "season": season, "names_included": include_names, "n": len(recs)}
    payload = json.dumps({"meta": meta, "profile": prof, "records": recs}, ensure_ascii=False).encode()
    salt = crypto.new_salt()
    key = crypto.derive_key(normalise_code(code), salt)
    nonce, ct = crypto.seal(key, payload, _aad())
    pkg = json.dumps({"app": "FinBridge", "type": "share", "v": VERSION, "n": crypto.KDF_N,
                      "salt": crypto.b64e(salt), "nonce": crypto.b64e(nonce), "ct": crypto.b64e(ct)},
                     separators=(",", ":"))
    return pkg, code


def claim(registry, meta: dict, now: datetime | None = None) -> None:
    """Mark an opened share as used. Raises Used when it was opened before (or carries no id to track)."""
    try:
        sid, exp = str(meta["id"]), datetime.fromisoformat(meta["expires"]).timestamp()
    except Exception as e:
        raise Used("no id") from e
    if not registry.claim(sid, exp, now.timestamp() if now else None):
        raise Used("already opened")


def open_package(pkg: str, code: str, now: datetime | None = None) -> tuple[dict, list[dict], dict]:
    """Returns (profile, records, meta). Raises Expired once the share's validity has passed, ShareError otherwise."""
    try:
        d = json.loads(pkg)
        if d.get("type") != "share" or d.get("v") != VERSION or d.get("n") != crypto.KDF_N:
            raise ValueError
        key = crypto.derive_key(normalise_code(code), crypto.b64d(d["salt"]))
        raw = crypto.unseal(key, crypto.b64d(d["nonce"]), crypto.b64d(d["ct"]), _aad())
        data = json.loads(raw)
        meta = data["meta"]
        expires = datetime.fromisoformat(meta["expires"])
    except Exception as e:
        raise ShareError("cannot open") from e
    if (now or _now()) > expires:                 # the expiry inside the encrypted data is the authoritative one
        raise Expired("expired")
    prof, recs, _ = R.parse_import(json.dumps({"profile": data.get("profile", {}), "records": data.get("records", [])}))
    return prof, recs, meta
