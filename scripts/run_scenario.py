#!/usr/bin/env python3
"""Ejecuta el escenario de autenticación AUTORIZADO contra un servidor del laboratorio.

Pasos (mismos en Apache y NGINX, para que los resultados sean comparables):
  S1  3 intentos fallidos consecutivos (contraseña incorrecta, usuario ficticio)
  S1b 4.º intento fallido  -> con control: bloqueado (429); sin control: 401
  S2  contraseña CORRECTA durante el bloqueo -> con control: 429; sin control: 302
  S3  contraseña correcta tras finalizar el bloqueo -> 302

Nunca guarda contraseñas. Solo usar contra el laboratorio (ver README, sección Seguridad).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

def wait_for_proxy(proxy: str | None, timeout: int = 180) -> None:
    """ZAP tarda en arrancar (descarga complementos): espera a que el proxy acepte conexiones."""
    if not proxy:
        return
    import socket
    u = urlparse(proxy)
    end = time.time() + timeout
    shown = False
    while time.time() < end:
        try:
            with socket.create_connection((u.hostname, u.port or 80), timeout=3):
                return
        except OSError:
            if not shown:
                print(f"[pre] esperando a que el proxy {proxy} (ZAP) esté listo...")
                shown = True
            time.sleep(3)
    raise SystemExit(f"El proxy {proxy} no respondió en {timeout}s; revise 'docker compose logs zap'.")


TARGETS = {"apache": "http://apache", "nginx": "http://nginx"}
ALLOWED_HOSTS = {"apache", "nginx", "localhost", "127.0.0.1"}
ALLOWED_SUFFIXES = (".lab.local",)
LOCK_MARK = "bloqueada temporalmente"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def check_lab_host(url: str) -> None:
    host = urlparse(url).hostname or ""
    if host not in ALLOWED_HOSTS and not host.endswith(ALLOWED_SUFFIXES):
        sys.exit(f"Destino no permitido: '{host}'. Este script solo puede apuntar al laboratorio.")


def attempt(base: str, user: str, password: str, proxy: str | None, run_id: str) -> dict:
    s = requests.Session()
    s.trust_env = False
    t0 = time.perf_counter()
    r = s.post(
        f"{base}/login",
        data={"username": user, "password": password},
        headers={"X-Lab-Run": run_id, "User-Agent": "lab-scenario/1.0"},
        proxies={"http": proxy, "https": proxy} if proxy else None,
        allow_redirects=False,
        timeout=15,
    )
    return {
        "http_status": r.status_code,
        "lock_message": LOCK_MARK in r.text,
        "retry_after": r.headers.get("Retry-After", ""),
        "backend": r.headers.get("X-Lab-Backend", ""),
        "location": r.headers.get("Location", ""),
        "elapsed_ms": round((time.perf_counter() - t0) * 1000),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", required=True, help="apache | nginx | URL del laboratorio")
    ap.add_argument("--mode", required=True, choices=["baseline", "hardened"],
                    help="Modo en que está corriendo la app (define los resultados esperados)")
    ap.add_argument("--user", default=os.getenv("LAB_USER", "usuario.demo"))
    ap.add_argument("--proxy", default=os.getenv("LAB_PROXY", ""), help="Proxy (OWASP ZAP), p. ej. http://zap:8090")
    ap.add_argument("--lock-seconds", type=int, default=int(os.getenv("LOCK_SECONDS", "120")))
    ap.add_argument("--out-dir", default="evidence/resultados")
    ap.add_argument("--run-id", default="")
    args = ap.parse_args()

    base = TARGETS.get(args.target, args.target).rstrip("/")
    check_lab_host(base)
    good = os.getenv("LAB_PASSWORD", "LabDemo#2026")
    bad = "clave-incorrecta-de-prueba"
    proxy = args.proxy or None
    label = args.target if args.target in TARGETS else urlparse(base).hostname
    run_id = args.run_id or f"{label}-{args.mode}-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}"
    hard = args.mode == "hardened"
    started = utcnow()

    wait_for_proxy(proxy)

    # Precondición: dejar la cuenta desbloqueada y con el contador en cero.
    for _ in range(3):
        pre = attempt(base, args.user, good, proxy, run_id + "-pre")
        if pre["http_status"] == 429:
            wait = int(pre["retry_after"] or args.lock_seconds) + 2
            print(f"[pre] cuenta bloqueada de una corrida anterior; esperando {wait}s...")
            time.sleep(wait)
            continue
        break
    if pre["http_status"] != 302:
        sys.exit(f"Precondición fallida (HTTP {pre['http_status']}). ¿Está bien LAB_PASSWORD / el servidor?")

    rows: list[dict] = []

    def step(name: str, n: int, kind: str, expected: int, expect_lock_msg: bool | None = None) -> None:
        res = attempt(base, args.user, good if kind == "correct" else bad, proxy, run_id)
        ok = res["http_status"] == expected and (expect_lock_msg is None or res["lock_message"] == expect_lock_msg)
        rows.append({"run_id": run_id, "target": label, "mode": args.mode, "step": name, "attempt_no": n,
                     "ts_utc": utcnow(), "username": args.user, "password_kind": kind,
                     "expected_status": expected, "http_status": res["http_status"],
                     "lock_message": res["lock_message"], "retry_after": res["retry_after"],
                     "backend": res["backend"], "elapsed_ms": res["elapsed_ms"], "passed": ok})

    for i in (1, 2, 3):
        step("S1 fallido consecutivo", i, "wrong", 401, expect_lock_msg=(hard and i == 3))
    step("S1b 4.º fallido", 4, "wrong", 429 if hard else 401)
    step("S2 correcta durante bloqueo", 5, "correct", 429 if hard else 302)
    if hard:
        wait = args.lock_seconds + 3
        print(f"[S3] esperando {wait}s a que termine el bloqueo...")
        time.sleep(wait)
    step("S3 correcta tras el bloqueo", 6, "correct", 302)

    finished = utcnow()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"run_id": run_id, "target": label, "base_url": base, "mode": args.mode, "proxy": proxy or "",
            "user": args.user, "lock_seconds": args.lock_seconds, "started": started, "finished": finished,
            "python": platform.python_version()}
    (out / f"{run_id}.json").write_text(json.dumps({"meta": meta, "attempts": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(out / f"{run_id}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"\nRun {run_id}  ({label}, modo {args.mode}, proxy: {proxy or 'no'})")
    print(f"{'paso':32} {'#':>2} {'esperado':>8} {'obtenido':>8} {'msg bloqueo':>11}  ok")
    for r in rows:
        print(f"{r['step']:32} {r['attempt_no']:>2} {r['expected_status']:>8} {r['http_status']:>8} {str(r['lock_message']):>11}  {'✔' if r['passed'] else '✘'}")
    bad_n = sum(not r["passed"] for r in rows)
    print(f"\nResultado: {'TODO COINCIDE CON LO ESPERADO' if not bad_n else f'{bad_n} paso(s) no coinciden'}")
    print(f"Archivos: {out / (run_id + '.json')} , {out / (run_id + '.csv')}")
    return 0 if not bad_n else 1


if __name__ == "__main__":
    raise SystemExit(main())
