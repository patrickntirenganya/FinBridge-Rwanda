"""Server-side account registry: one document per phone number, so a number can be claimed only once and a
returning farmer signs in from any device. Channel-agnostic and free of any UI.

What the server holds per account: the encrypted vault (AES-256-GCM, key derived from phone + PIN, so the server
cannot read it), and the wrong-PIN counter. It never sees a PIN, a key or a plaintext record. The document id is an
HMAC of the phone number, so the database does not list phone numbers.

Honest limit: whoever can read the database can copy vaults and guess PINs offline (see docs/security.md), and
the phone number is not proven by SMS yet (demo one-time code), so the first person to register a number owns it.
"""
from __future__ import annotations
import hashlib
import hmac


class AccountError(Exception):
    """The registry could not be reached. Callers fall back to browser-only storage."""


class Memory:
    """In-memory backend for tests and local runs without Firebase."""

    def __init__(self):
        self.docs: dict[str, dict] = {}

    def get(self, doc_id):
        d = self.docs.get(doc_id)
        return dict(d) if d is not None else None

    def create(self, doc_id, data) -> bool:
        if doc_id in self.docs:
            return False
        self.docs[doc_id] = dict(data)
        return True

    def update(self, doc_id, data):
        if doc_id in self.docs:
            self.docs[doc_id].update(data)


class Firestore:
    """Cloud Firestore backend. `info` is the service-account dict from Streamlit Secrets, never from the repo."""

    def __init__(self, info: dict, collection: str = "accounts"):
        from google.api_core.exceptions import AlreadyExists
        from google.cloud import firestore                      # imported late: the app runs without it
        from google.oauth2 import service_account
        info = {k: v for k, v in dict(info).items() if k != "account_pepper"}
        info.setdefault("type", "service_account")
        info["private_key"] = str(info.get("private_key", "")).replace("\\n", "\n")
        info.setdefault("token_uri", "https://oauth2.googleapis.com/token")
        creds = service_account.Credentials.from_service_account_info(info)
        self._col = firestore.Client(project=info["project_id"], credentials=creds).collection(collection)
        self._exists = AlreadyExists

    def get(self, doc_id):
        snap = self._col.document(doc_id).get()
        return snap.to_dict() if snap.exists else None

    def create(self, doc_id, data) -> bool:
        try:
            self._col.document(doc_id).create(data)             # fails if the document exists: one claim per number
            return True
        except self._exists:
            return False

    def update(self, doc_id, data):
        self._col.document(doc_id).update(data)


class Accounts:
    def __init__(self, backend, pepper: str = ""):
        self._b = backend
        self._pepper = (pepper or "finbridge-accounts-v1").encode()

    def _id(self, phone: str) -> str:
        return hmac.new(self._pepper, phone.encode(), hashlib.sha256).hexdigest()

    def _run(self, fn, *a):
        try:
            return fn(*a)
        except Exception as e:                                   # network, permission, quota
            raise AccountError(str(e)) from e

    def get(self, phone: str) -> dict | None:
        """{'vault': str, 'fails': int, 'until': float} or None when no account exists."""
        d = self._run(self._b.get, self._id(phone))
        if not d or not isinstance(d.get("vault"), str):
            return None
        return {"vault": d["vault"], "fails": int(d.get("fails", 0)), "until": float(d.get("until", 0.0))}

    def create(self, phone: str, vault: str) -> bool:
        """True if the number was free and is now claimed; False if an account already exists."""
        return bool(self._run(self._b.create, self._id(phone), {"vault": vault, "fails": 0, "until": 0.0}))

    def save(self, phone: str, vault: str) -> None:
        self._run(self._b.update, self._id(phone), {"vault": vault})

    def set_lock(self, phone: str, lock: dict) -> None:
        self._run(self._b.update, self._id(phone),
                  {"fails": int(lock.get("fails", 0)), "until": float(lock.get("until", 0.0))})
