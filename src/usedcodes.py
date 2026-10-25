"""Registry of share codes that have already been opened, so a code works once.

DEMO LIMIT: this lives in the server process's memory. It enforces one opening per code while the app keeps running
but is forgotten on a restart, and a lender cannot be told apart from another. A database table (share id,
opened-at, institution) replaces it without changing callers. Kept here, free of any UI, so it can be tested.
"""
from __future__ import annotations
import threading
import time


class Registry:
    def __init__(self):
        self._lock = threading.Lock()
        self._used: dict[str, float] = {}

    def claim(self, share_id: str, expires_at: float, now: float | None = None) -> bool:
        """True the first time an id is claimed, False after. The check and the mark are one atomic step."""
        now = time.time() if now is None else now
        with self._lock:
            self._used = {k: v for k, v in self._used.items() if v > now}      # forget ids past their expiry
            if share_id in self._used:
                return False
            self._used[share_id] = max(expires_at, now + 60)
            return True
