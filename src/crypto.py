"""Cryptographic primitives for FinBridge: scrypt key derivation and AES-256-GCM authenticated encryption.

Nothing here knows about farmers or loans. Callers pass a secret (PIN or share code), a random salt and
associated data (AAD) that binds the ciphertext to its purpose, so a vault cannot be opened as a share.
A wrong secret, a wrong AAD or any tampering raises CryptoError with no further detail.
"""
from __future__ import annotations
import base64
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

KDF_N = 2 ** 16          # 64 MB, about 0.4 s per guess on a laptop; raises the cost of offline guessing
KDF_R, KDF_P = 8, 1
SALT_BYTES, NONCE_BYTES = 16, 12


class CryptoError(Exception):
    """Wrong secret, wrong purpose or damaged data. Deliberately uninformative."""


def b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("ascii")


def b64d(s: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(s.encode("ascii"))
    except Exception as e:
        raise CryptoError("bad encoding") from e


def new_salt() -> bytes:
    return os.urandom(SALT_BYTES)


def derive_key(secret: str, salt: bytes, n: int = KDF_N) -> bytes:
    return Scrypt(salt=salt, length=32, n=n, r=KDF_R, p=KDF_P).derive(secret.encode("utf-8"))


def seal(key: bytes, plaintext: bytes, aad: bytes) -> tuple[bytes, bytes]:
    """Encrypt with a fresh random nonce. Returns (nonce, ciphertext+tag)."""
    nonce = os.urandom(NONCE_BYTES)
    return nonce, AESGCM(key).encrypt(nonce, plaintext, aad)


def unseal(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, aad)
    except (InvalidTag, ValueError) as e:
        raise CryptoError("cannot decrypt") from e
