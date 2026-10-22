#!/usr/bin/env python3
"""Genera el código QR del mensaje de phishing SIMULADO.

Seguridad: solo acepta URL del laboratorio (apache, nginx, localhost, *.lab.local).
Un QR hacia un sitio externo está prohibido por las reglas de la práctica.
"""
import argparse
import sys
from urllib.parse import urlparse

import qrcode

ALLOWED_HOSTS = {"apache", "nginx", "localhost", "127.0.0.1"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url", help="p. ej. http://apache/r/qr1")
    ap.add_argument("--out", default="phishing/qr_apache.png")
    a = ap.parse_args()
    host = urlparse(a.url).hostname or ""
    if host not in ALLOWED_HOSTS and not host.endswith(".lab.local"):
        sys.exit(f"Rechazado: '{host}' no pertenece al laboratorio.")
    qrcode.make(a.url).save(a.out)
    print(f"QR para {a.url} guardado en {a.out}")


if __name__ == "__main__":
    main()
