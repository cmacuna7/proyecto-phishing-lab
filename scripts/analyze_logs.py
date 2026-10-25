#!/usr/bin/env python3
"""Analiza y correlaciona los registros del laboratorio (informe 3.5.1).

Fuentes: registro de auditoría de la app (JSON Lines), access.log de Apache y NGINX
(formato 'combined') y, opcionalmente, el CSV exportado de OWASP ZAP.

Distingue lo OBSERVADO (conteos, horas, IP) de lo INTERPRETADO (ver sección final).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ACCESS_RE = re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+)[^"]*" (\d{3}) (\S+) "[^"]*" "([^"]*)"')


def read_audit(paths, run_id=""):
    ev = []
    for p in paths:
        for line in Path(p).read_text(encoding="utf-8").splitlines():
            if line.strip():
                e = json.loads(line)
                if not run_id or e.get("run_id", "").startswith(run_id) or e["event"] == "LOCKOUT_END":
                    ev.append(e)
    return sorted(ev, key=lambda e: e["ts"])


def read_access(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = ACCESS_RE.match(line)
        if not m:
            continue
        ip, ts, method, url, status, _size, ua = m.groups()
        t = datetime.strptime(ts, "%d/%b/%Y:%H:%M:%S %z").astimezone(timezone.utc)
        rows.append({"ip": ip, "ts": t.isoformat(timespec="seconds").replace("+00:00", "Z"),
                     "method": method, "url": url, "status": int(status), "ua": ua})
    return rows


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows (cp1252) no imprime → ni ✔
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--audit", nargs="*", default=[], help="auth.log de la app (uno o más)")
    ap.add_argument("--access", nargs="*", default=[], metavar="ETIQUETA=ARCHIVO", help="p. ej. apache=logs/apache/access.log")
    ap.add_argument("--zap-csv", default="", help="CSV generado por zap_export.py")
    ap.add_argument("--run-id", default="", help="Filtra la auditoría por prefijo de run_id")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    L = ["# Análisis de registros", ""]
    ev = read_audit(a.audit, a.run_id) if a.audit else []
    attempts = [e for e in ev if e["event"] in ("LOGIN_SUCCESS", "LOGIN_FAILED", "LOGIN_BLOCKED")]

    if ev:
        L += ["## 1. Registro de auditoría de la aplicación (observado)", "",
              md_table(["Evento", "Cantidad"], sorted(Counter(e["event"] for e in ev).items())), "",
              f"- Intentos de autenticación registrados: **{len(attempts)}** "
              f"(éxitos {sum(e['event']=='LOGIN_SUCCESS' for e in attempts)}, "
              f"fallidos {sum(e['event']=='LOGIN_FAILED' for e in attempts)}, "
              f"bloqueados {sum(e['event']=='LOGIN_BLOCKED' for e in attempts)})",
              f"- Usuarios ficticios involucrados: {sorted({e['username'] for e in attempts if e['username']})}",
              f"- IP de origen vistas por la app: {sorted({e['src_ip'] for e in ev if e['src_ip']})}",
              f"- Rango de tiempo: {ev[0]['ts']} → {ev[-1]['ts']}", "",
              "### Secuencia (línea de tiempo)", "",
              md_table(["Hora (UTC)", "Evento", "Usuario", "Resultado", "IP", "Fallos", "Estado cuenta"],
                       [(e["ts"], e["event"], e["username"], e["result"], e["src_ip"],
                         "" if e["failed_count"] is None else e["failed_count"], e["lock_state"]) for e in ev[:80]]), ""]
        starts = [e for e in ev if e["event"] == "LOCKOUT_START"]
        ends = [e for e in ev if e["event"] == "LOCKOUT_END"]
        L += [f"- Bloqueos activados: **{len(starts)}**; finalizados: **{len(ends)}**", ""]

    web = {}
    for item in a.access:
        label, _, path = item.partition("=")
        rows = [r for r in read_access(path) if r["method"] == "POST" and r["url"].split("?")[0] == "/login"]
        web[label] = rows
    if web:
        L += ["## 2. Registros de acceso de los servidores web (observado)", ""]
        for label, rows in web.items():
            L += [f"### {label}", "",
                  md_table(["Código HTTP", "POST /login"], sorted(Counter(r["status"] for r in rows).items())), "",
                  f"- IP de origen vistas por el servidor: {sorted({r['ip'] for r in rows})}", ""]

    zap = []
    if a.zap_csv:
        with open(a.zap_csv, newline="", encoding="utf-8") as fh:
            zap = [r for r in csv.DictReader(fh) if r["method"] == "POST" and r["url"].split("?")[0].endswith("/login")]
        L += ["## 3. Solicitudes capturadas por OWASP ZAP (observado)", "",
              md_table(["Código HTTP", "POST /login"], sorted(Counter(r["status"] for r in zap).items())), ""]

    L += ["## 4. Correlación de conteos", ""]
    corr = []
    if ev:
        corr.append(("Auditoría de la app", len(attempts)))
    corr += [(f"access.log {k}", len(v)) for k, v in web.items()]
    if a.zap_csv:
        corr.append(("OWASP ZAP", len(zap)))
    L += [md_table(["Fuente", "Intentos de login contados"], corr), "",
          "Si los números difieren, revise: pruebas previas en el mismo log, la precondición del script "
          "(1 login correcto previo), filtros de `--run-id` y que ZAP solo ve el tráfico que pasa por su proxy.", "",
          "## 5. Observado vs. interpretado", "",
          "- **Observado:** conteos, códigos HTTP, horas, IP y estado de bloqueo que aparecen en los archivos.",
          "- **Interpretación (debe justificarse):** una IP por sí sola no demuestra que el intento venga de un atacante, "
          "ni si el origen es interno o externo. Cuando el tráfico pasa por ZAP, el servidor ve la IP de ZAP, no la del cliente.",
          "- Las diferencias entre ZAP y los servidores se explican por el punto de captura (proxy vs. servidor vs. aplicación), "
          "no necesariamente por errores."]

    text = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"Reporte escrito en {a.out}")
    print(text)


if __name__ == "__main__":
    main()
