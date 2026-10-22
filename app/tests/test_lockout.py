"""Pruebas del control de bloqueo temporal y del registro de auditoría.

Ejecutar:  cd app && python -m pytest -q
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from labapp import Config, create_app  # noqa: E402

USER = "usuario.demo"
GOOD = "LabDemo#2026"
BAD = "clave-incorrecta-xyz"


class Clock:
    def __init__(self):
        self.t = datetime(2026, 10, 22, 15, 0, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += timedelta(seconds=seconds)


def make(tmp_path, mode="hardened", **kw):
    clock = Clock()
    cfg = Config(
        server_label="test", controls_mode=mode, lock_seconds=120,
        db_path=str(tmp_path / "u.db"), audit_log_path=str(tmp_path / "auth.log"),
        secret_key="t", lab_user=USER, lab_password=GOOD, **kw,
    )
    app = create_app(cfg, now_fn=clock)
    return app, app.test_client(), clock, tmp_path / "auth.log"


def login(client, user=USER, pwd=GOOD, **headers):
    return client.post("/login", data={"username": user, "password": pwd}, headers=headers)


def events(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_success_is_redirected_and_logged(tmp_path):
    _, c, _, log = make(tmp_path)
    r = login(c)
    assert r.status_code == 302 and r.headers["Location"].endswith("/panel")
    ev = events(log)
    assert [e["event"] for e in ev] == ["LOGIN_SUCCESS"]
    assert ev[0]["username"] == USER and ev[0]["result"] == "SUCCESS" and ev[0]["lock_state"] == "unlocked"
    assert ev[0]["ts"].endswith("Z") and ev[0]["src_ip"]


def test_three_consecutive_failures_lock_the_account(tmp_path):
    _, c, _, log = make(tmp_path)
    rs = [login(c, pwd=BAD) for _ in range(3)]
    assert [r.status_code for r in rs] == [401, 401, 401]
    assert "bloqueada temporalmente" not in rs[1].get_data(as_text=True)
    assert "bloqueada temporalmente" in rs[2].get_data(as_text=True)   # el 3.º fallo informa el bloqueo
    names = [e["event"] for e in events(log)]
    assert names == ["LOGIN_FAILED", "LOGIN_FAILED", "LOGIN_FAILED", "LOCKOUT_START"]
    start = events(log)[-1]
    assert start["lock_state"] == "locked" and start["lock_remaining_s"] == 120 and start["locked_until"]


def test_correct_password_is_rejected_while_locked(tmp_path):
    _, c, clock, log = make(tmp_path)
    for _ in range(3):
        login(c, pwd=BAD)
    clock.advance(30)
    r = login(c, pwd=GOOD)
    assert r.status_code == 429
    assert r.headers["Retry-After"] == "90"
    assert "bloqueada temporalmente" in r.get_data(as_text=True)
    assert events(log)[-1]["event"] == "LOGIN_BLOCKED"
    # no se creó sesión: /panel redirige a /login
    assert c.get("/panel").status_code == 302


def test_attempts_during_lock_do_not_extend_it(tmp_path):
    _, c, clock, _ = make(tmp_path)
    for _ in range(3):
        login(c, pwd=BAD)
    clock.advance(100)
    assert login(c, pwd=BAD).status_code == 429
    clock.advance(21)  # total 121 s desde el bloqueo
    assert login(c, pwd=GOOD).status_code == 302


def test_login_works_after_lock_expires_and_end_is_logged(tmp_path):
    _, c, clock, log = make(tmp_path)
    for _ in range(3):
        login(c, pwd=BAD)
    clock.advance(121)
    assert login(c, pwd=GOOD).status_code == 302
    names = [e["event"] for e in events(log)]
    assert names[-2:] == ["LOCKOUT_END", "LOGIN_SUCCESS"]
    end = [e for e in events(log) if e["event"] == "LOCKOUT_END"][0]
    start = [e for e in events(log) if e["event"] == "LOCKOUT_START"][0]
    assert end["ts"] == start["locked_until"]  # el fin se registra a la hora real de vencimiento


def test_sweeper_logs_lockout_end_once(tmp_path):
    app, c, clock, log = make(tmp_path)
    auth = app.extensions["lab_auth"]
    for _ in range(3):
        login(c, pwd=BAD)
    assert auth.release_expired() == []
    clock.advance(121)
    assert auth.release_expired() == [USER]
    assert auth.release_expired() == []
    assert [e["event"] for e in events(log)].count("LOCKOUT_END") == 1


def test_success_resets_the_failure_counter(tmp_path):
    _, c, _, log = make(tmp_path)
    login(c, pwd=BAD); login(c, pwd=BAD)
    assert login(c).status_code == 302
    login(c, pwd=BAD); login(c, pwd=BAD)
    assert "LOCKOUT_START" not in [e["event"] for e in events(log)]


def test_failures_must_be_consecutive_to_lock(tmp_path):
    _, c, _, log = make(tmp_path)
    for _ in range(2):
        login(c, pwd=BAD)
    login(c)  # éxito en medio
    for _ in range(2):
        login(c, pwd=BAD)
    assert login(c).status_code == 302


def test_unknown_user_fails_without_creating_state_and_is_marked(tmp_path):
    _, c, _, log = make(tmp_path)
    for _ in range(5):
        assert login(c, user="no.existe", pwd=BAD).status_code == 401
    ev = events(log)
    assert all(e["event"] == "LOGIN_FAILED" and e["user_known"] is False for e in ev)
    assert login(c).status_code == 302  # la cuenta real no se afecta


def test_passwords_never_reach_the_audit_log(tmp_path):
    _, c, _, log = make(tmp_path)
    secret = "S3cretoUnico!987"
    login(c, pwd=secret)
    login(c, pwd=BAD)
    login(c)
    for _ in range(3):
        login(c, pwd=BAD)
    text = log.read_text(encoding="utf-8")
    for s in (secret, BAD, GOOD, "password"):
        assert s not in text


def test_log_injection_is_neutralised(tmp_path):
    _, c, _, log = make(tmp_path)
    login(c, user='x"\n{"event":"LOGIN_SUCCESS"}', pwd=BAD)
    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["event"] == "LOGIN_FAILED"


def test_baseline_mode_has_no_lockout_and_no_audit_log(tmp_path):
    _, c, _, log = make(tmp_path, mode="baseline")
    assert [login(c, pwd=BAD).status_code for _ in range(6)] == [401] * 6
    assert login(c).status_code == 302   # sigue permitiendo entrar: no hay bloqueo
    assert not log.exists()


def test_short_link_redirects_only_to_local_login_and_logs_ref(tmp_path):
    _, c, _, log = make(tmp_path)
    r = c.get("/r/qr1")
    assert r.status_code == 302 and r.headers["Location"] == "/login?ref=afiche-qr"
    assert events(log)[-1]["event"] == "LINK_VISIT" and events(log)[-1]["ref"] == "afiche-qr"
    assert c.get("/r/https://evil.example").status_code == 404
    assert c.get("/r/desconocido").status_code == 404


def test_run_id_header_is_recorded_for_correlation(tmp_path):
    _, c, _, log = make(tmp_path)
    login(c, pwd=BAD, **{"X-Lab-Run": "run-001"})
    assert events(log)[-1]["run_id"] == "run-001"


def test_proxy_header_gives_client_ip_when_behind_trusted_proxy(tmp_path):
    clock = Clock()
    cfg = Config(server_label="t", db_path=str(tmp_path / "u.db"), audit_log_path=str(tmp_path / "a.log"),
                 secret_key="t", lab_user=USER, lab_password=GOOD, trusted_proxy_hops=1)
    c = create_app(cfg, now_fn=clock).test_client()
    # un cliente malicioso intenta falsear la IP; el proxy de confianza añade la real al final
    login(c, pwd=BAD, **{"X-Forwarded-For": "6.6.6.6, 10.0.0.7"})
    ev = events(tmp_path / "a.log")[-1]
    assert ev["src_ip"] == "10.0.0.7"


def test_failed_login_page_does_not_reveal_whether_user_exists(tmp_path):
    _, c, _, _ = make(tmp_path)
    a = login(c, user="no.existe", pwd=BAD).get_data(as_text=True)
    b = login(c, pwd=BAD).get_data(as_text=True)
    assert "Usuario o contraseña incorrectos." in a and "Usuario o contraseña incorrectos." in b
