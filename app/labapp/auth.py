"""Almacén de usuarios (SQLite) y lógica de autenticación con bloqueo temporal.

Control implementado: tras N intentos fallidos CONSECUTIVOS (por defecto 3) la
cuenta se bloquea durante `lock_seconds`. Durante el bloqueo no se evalúa la
contraseña: incluso la correcta es rechazada. Un inicio de sesión exitoso
reinicia el contador.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

from .audit import AuditLogger
from .config import Config

SUCCESS, FAILED, BLOCKED = "SUCCESS", "FAILED", "BLOCKED"
_PBKDF2_ROUNDS = 200_000


def _hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ROUNDS)


@dataclass
class AttemptResult:
    status: str                      # SUCCESS | FAILED | BLOCKED
    lock_remaining_s: int = 0
    failed_count: int = 0
    locked_now: bool = False         # este intento activó el bloqueo


class AuthService:
    def __init__(self, cfg: Config, audit: AuditLogger, now_fn: Callable[[], datetime] | None = None):
        self.cfg = cfg
        self.audit = audit
        self.now = now_fn or (lambda: datetime.now(timezone.utc))
        os.makedirs(os.path.dirname(cfg.db_path) or ".", exist_ok=True)
        self._init_db()
        self._dummy_salt = os.urandom(16)

    # ---------------------------------------------------------------- db
    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.cfg.db_path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._conn() as c:
            c.execute(
                """CREATE TABLE IF NOT EXISTS users (
                       username TEXT PRIMARY KEY,
                       salt BLOB NOT NULL,
                       pwd_hash BLOB NOT NULL,
                       failed_count INTEGER NOT NULL DEFAULT 0,
                       locked_until TEXT
                   )"""
            )
            row = c.execute("SELECT 1 FROM users WHERE username=?", (self.cfg.lab_user,)).fetchone()
            if row is None:
                salt = os.urandom(16)
                c.execute(
                    "INSERT INTO users(username, salt, pwd_hash) VALUES (?,?,?)",
                    (self.cfg.lab_user, salt, _hash(self.cfg.lab_password, salt)),
                )

    @staticmethod
    def _parse(ts: str | None) -> datetime | None:
        return datetime.fromisoformat(ts) if ts else None

    # ---------------------------------------------------------- attempts
    def attempt(self, username: str, password: str, src_ip: str, *, run_id: str = "", request_id: str = "") -> AttemptResult:
        now = self.now()
        common = dict(src_ip=src_ip, run_id=run_id, request_id=request_id)
        ctrl = self.cfg.controls_enabled

        conn = self._conn()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

            if row is None:
                # Usuario desconocido: se gasta el mismo tiempo de hash y se responde igual.
                _hash(password, self._dummy_salt)
                conn.execute("COMMIT")
                self.audit.record("LOGIN_FAILED", now, username=username, result=FAILED,
                                  user_known=False, lock_state="unlocked", **common)
                return AttemptResult(FAILED)

            locked_until = self._parse(row["locked_until"])
            failed = row["failed_count"]
            events: list[tuple] = []

            if ctrl and locked_until is not None:
                if now < locked_until:
                    remaining = max(1, int((locked_until - now).total_seconds() + 0.999))
                    conn.execute("COMMIT")
                    self.audit.record("LOGIN_BLOCKED", now, username=username, result=BLOCKED,
                                      user_known=True, failed_count=failed, lock_state="locked",
                                      lock_remaining_s=remaining, locked_until=locked_until, **common)
                    return AttemptResult(BLOCKED, lock_remaining_s=remaining, failed_count=failed)
                # El bloqueo ya venció y nadie lo cerró todavía: se cierra aquí.
                conn.execute("UPDATE users SET failed_count=0, locked_until=NULL WHERE username=?", (username,))
                events.append(("LOCKOUT_END", dict(username=username, result="INFO", user_known=True,
                                                   failed_count=0, lock_state="unlocked",
                                                   locked_until=locked_until, ts=locked_until)))
                failed = 0

            ok = hmac.compare_digest(_hash(password, bytes(row["salt"])), bytes(row["pwd_hash"]))

            if ok:
                if ctrl:
                    conn.execute("UPDATE users SET failed_count=0, locked_until=NULL WHERE username=?", (username,))
                conn.execute("COMMIT")
                for name, kw in events:
                    self._emit(name, now, common, kw)
                self.audit.record("LOGIN_SUCCESS", now, username=username, result=SUCCESS,
                                  user_known=True, failed_count=0, lock_state="unlocked", **common)
                return AttemptResult(SUCCESS)

            if not ctrl:
                conn.execute("COMMIT")
                for name, kw in events:
                    self._emit(name, now, common, kw)
                self.audit.record("LOGIN_FAILED", now, username=username, result=FAILED,
                                  user_known=True, lock_state="unlocked", **common)
                return AttemptResult(FAILED)

            failed += 1
            locked_now = failed >= self.cfg.max_failed_attempts
            new_until = now + timedelta(seconds=self.cfg.lock_seconds) if locked_now else None
            conn.execute(
                "UPDATE users SET failed_count=?, locked_until=? WHERE username=?",
                (failed, new_until.isoformat() if new_until else None, username),
            )
            conn.execute("COMMIT")
            for name, kw in events:
                self._emit(name, now, common, kw)
            self.audit.record("LOGIN_FAILED", now, username=username, result=FAILED, user_known=True,
                              failed_count=failed, lock_state="locked" if locked_now else "unlocked", **common)
            if locked_now:
                self.audit.record("LOCKOUT_START", now, username=username, result="INFO", user_known=True,
                                  failed_count=failed, lock_state="locked",
                                  lock_remaining_s=self.cfg.lock_seconds, locked_until=new_until, **common)
            return AttemptResult(FAILED, failed_count=failed, locked_now=locked_now,
                                 lock_remaining_s=self.cfg.lock_seconds if locked_now else 0)
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        finally:
            conn.close()

    def _emit(self, name: str, now: datetime, common: dict, kw: dict) -> None:
        kw = dict(kw)
        ts = kw.pop("ts", now)
        self.audit.record(name, ts, **kw, src_ip="", run_id="", request_id="")

    # ----------------------------------------------------------- sweeper
    def release_expired(self) -> list[str]:
        """Cierra los bloqueos vencidos y registra LOCKOUT_END (a su hora real)."""
        if not self.cfg.controls_enabled:
            return []
        now = self.now()
        released: list[tuple[str, datetime]] = []
        conn = self._conn()
        try:
            conn.execute("BEGIN IMMEDIATE")
            rows = conn.execute("SELECT username, locked_until FROM users WHERE locked_until IS NOT NULL").fetchall()
            for r in rows:
                until = self._parse(r["locked_until"])
                if until is not None and until <= now:
                    conn.execute("UPDATE users SET failed_count=0, locked_until=NULL WHERE username=?", (r["username"],))
                    released.append((r["username"], until))
            conn.execute("COMMIT")
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        finally:
            conn.close()
        for username, until in released:
            self.audit.record("LOCKOUT_END", until, username=username, result="INFO", user_known=True,
                              failed_count=0, lock_state="unlocked", locked_until=until)
        return [u for u, _ in released]
