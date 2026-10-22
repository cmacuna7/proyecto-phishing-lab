"""Registro de auditoría de eventos de autenticación (JSON Lines).

Regla de diseño: este módulo NO recibe contraseñas, tokens ni cookies. La
función `record` solo acepta campos de una lista cerrada, de modo que un
secreto no puede llegar al archivo por error.
"""
from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime, timezone

EVENTS = {
    "LINK_VISIT",      # visita a un enlace/QR de la campaña simulada
    "LOGIN_SUCCESS",
    "LOGIN_FAILED",
    "LOGIN_BLOCKED",   # intento mientras la cuenta está bloqueada
    "LOCKOUT_START",
    "LOCKOUT_END",
}

_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def clean(value, max_len: int = 64) -> str:
    """Quita caracteres de control y limita el largo (evita inyección en logs)."""
    return _CONTROL.sub("?", str(value))[:max_len]


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class AuditLogger:
    def __init__(self, path: str, server_label: str, enabled: bool = True):
        self.path = path
        self.server = server_label
        self.enabled = enabled
        self._lock = threading.Lock()
        if enabled:
            os.makedirs(os.path.dirname(path), exist_ok=True)

    def record(
        self,
        event: str,
        now: datetime,
        *,
        username: str = "",
        result: str = "",
        src_ip: str = "",
        user_known: bool | None = None,
        failed_count: int | None = None,
        lock_state: str = "",
        lock_remaining_s: int | None = None,
        locked_until: datetime | None = None,
        ref: str = "",
        run_id: str = "",
        request_id: str = "",
    ) -> None:
        if not self.enabled:
            return
        if event not in EVENTS:
            raise ValueError(f"evento no permitido: {event}")
        entry = {
            "ts": iso(now),
            "event": event,
            "username": clean(username),
            "result": result,
            "src_ip": clean(src_ip, 45),
            "user_known": user_known,
            "failed_count": failed_count,
            "lock_state": lock_state,
            "lock_remaining_s": lock_remaining_s,
            "locked_until": iso(locked_until) if locked_until else None,
            "server": self.server,
            "ref": clean(ref, 32),
            "run_id": clean(run_id, 40),
            "request_id": clean(request_id, 40),
        }
        line = json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
