#!/usr/bin/env python3
"""Exporta el historial de OWASP ZAP (API REST) a CSV, SIN contraseñas.

Uso típico (desde un cliente del laboratorio o la máquina de monitoreo):
    python scripts/zap_export.py --zap http://zap:8090 --baseurl http://apache --out evidence/corridas/<corrida>/zap/apache_hardened.csv

El cuerpo de las solicitudes se descarta: solo se conserva el nombre de los campos del
formulario con su valor enmascarado (password=***). Así el CSV puede ir al repositorio.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def api(zap: str, path: str, **params):
    url = f"{zap.rstrip('/')}{path}?{urllib.parse.urlencode(params)}"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # hablar directo con ZAP
    with opener.open(url, timeout=30) as r:
        return r.read()


def redact_body(body: str) -> str:
    """Conserva solo la estructura del formulario; enmascara todos los valores."""
    return "&".join(f"{k}=***" for k, _, _ in (p.partition("=") for p in body.split("&") if p))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zap", default="http://zap:8090")
    ap.add_argument("--baseurl", default="", help="Filtrar por URL base (p. ej. http://nginx)")
    ap.add_argument("--out", default="evidence/corridas/sin-nombre/zap/zap_history.csv")
    ap.add_argument("--report", default="", help="Ruta para guardar además el reporte HTML de ZAP")
    a = ap.parse_args()

    rows, start, page = [], 0, 500
    while True:
        data = json.loads(api(a.zap, "/JSON/core/view/messages/", baseurl=a.baseurl, start=start, count=page))
        msgs = data.get("messages", [])
        for m in msgs:
            req_head = m.get("requestHeader", "")
            first = req_head.split("\r\n", 1)[0].split(" ")
            method, url = (first + ["", ""])[:2]
            status = re.search(r"HTTP/\S+ (\d{3})", m.get("responseHeader", "") or "")
            run = re.search(r"(?im)^X-Lab-Run:\s*(.+?)\s*$", req_head)
            ts = datetime.fromtimestamp(int(m["timestamp"]) / 1000, tz=timezone.utc)
            rows.append({
                "id": m["id"], "ts_utc": ts.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                "method": method, "url": url, "status": status.group(1) if status else "",
                "rtt_ms": m.get("rtt", ""), "x_lab_run": run.group(1) if run else "",
                "form_fields_redacted": redact_body(m.get("requestBody", "") or ""),
            })
        if len(msgs) < page:
            break
        start += page

    rows.sort(key=lambda r: r["ts_utc"])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "ts_utc", "method", "url", "status", "rtt_ms", "x_lab_run", "form_fields_redacted"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} mensajes exportados a {a.out}")

    if a.report:
        Path(a.report).parent.mkdir(parents=True, exist_ok=True)
        Path(a.report).write_bytes(api(a.zap, "/OTHER/core/other/htmlreport/"))
        print(f"Reporte HTML de ZAP en {a.report}")


if __name__ == "__main__":
    main()
