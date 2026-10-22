"""Aplicación de prueba del laboratorio de phishing y monitoreo.

SOLO PARA USO ACADÉMICO EN EL LABORATORIO AUTORIZADO. Cuenta y datos ficticios.
"""
from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Callable

from flask import Flask, abort, redirect, render_template, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

from .audit import AuditLogger, clean
from .auth import BLOCKED, SUCCESS, AuthService
from .config import Config

# Enlaces "acortados" del laboratorio: solo redirigen a /login de ESTA aplicación.
LINK_CODES = {
    "qr1": "afiche-qr",
    "mail1": "correo-simulado",
}

__all__ = ["create_app", "Config"]


def create_app(cfg: Config | None = None, now_fn: Callable[[], datetime] | None = None,
               start_sweeper: bool = False) -> Flask:
    cfg = cfg or Config.from_env()
    now = now_fn or (lambda: datetime.now(timezone.utc))

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=cfg.secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if cfg.trusted_proxy_hops > 0:
        # Detrás de Apache/NGINX: toma la IP que el proxy de confianza añadió (último salto).
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=cfg.trusted_proxy_hops, x_proto=cfg.trusted_proxy_hops)

    audit = AuditLogger(cfg.audit_log_path, cfg.server_label, enabled=cfg.controls_enabled)
    auth = AuthService(cfg, audit, now_fn=now)
    app.extensions["lab_auth"] = auth
    app.extensions["lab_cfg"] = cfg

    @app.after_request
    def _headers(resp):
        resp.headers["X-Lab-Backend"] = cfg.server_label
        resp.headers["Cache-Control"] = "no-store"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        return resp

    def _ctx(**extra):
        return dict(server=cfg.server_label, mode=cfg.controls_mode, **extra)

    @app.get("/")
    def index():
        return redirect(url_for("login"))

    @app.get("/healthz")
    def healthz():
        return "ok", 200, {"Content-Type": "text/plain; charset=utf-8"}

    @app.get("/r/<code>")
    def short_link(code: str):
        tag = LINK_CODES.get(code)
        if tag is None:
            abort(404)
        audit.record("LINK_VISIT", now(), result="INFO", src_ip=request.remote_addr or "",
                     ref=tag, run_id=request.headers.get("X-Lab-Run", ""))
        return redirect(url_for("login", ref=tag), code=302)

    @app.get("/login")
    def login():
        return render_template("login.html", **_ctx(message=None, ref=clean(request.args.get("ref", ""), 32)))

    @app.post("/login")
    def login_post():
        username = clean(request.form.get("username", "").strip())
        password = request.form.get("password", "")
        run_id = request.headers.get("X-Lab-Run", "")
        request_id = uuid.uuid4().hex[:12]
        res = auth.attempt(username, password, request.remote_addr or "", run_id=run_id, request_id=request_id)

        if res.status == SUCCESS:
            session.clear()
            session["user"] = username
            return redirect(url_for("panel"), code=302)
        if res.status == BLOCKED:
            msg = f"Cuenta bloqueada temporalmente. Intente de nuevo en {res.lock_remaining_s} segundos."
            return (render_template("login.html", **_ctx(message=msg, kind="locked", ref="")), 429,
                    {"Retry-After": str(res.lock_remaining_s)})
        msg = "Usuario o contraseña incorrectos."
        kind = "error"
        if res.locked_now:
            msg += f" Por seguridad, la cuenta quedó bloqueada temporalmente ({res.lock_remaining_s} segundos)."
            kind = "locked"
        return render_template("login.html", **_ctx(message=msg, kind=kind, ref="")), 401

    @app.get("/panel")
    def panel():
        user = session.get("user")
        if not user:
            return redirect(url_for("login"))
        return render_template("panel.html", **_ctx(user=user))

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    if start_sweeper and cfg.controls_enabled:
        stop = threading.Event()

        def _loop():
            while not stop.wait(cfg.sweeper_interval):
                try:
                    auth.release_expired()
                except Exception:  # el barrido nunca debe tumbar la app
                    app.logger.exception("fallo en release_expired")

        t = threading.Thread(target=_loop, name="lockout-sweeper", daemon=True)
        t.start()
        app.extensions["lab_sweeper_stop"] = stop

    return app
