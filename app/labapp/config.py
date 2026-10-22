"""Configuración de la aplicación de prueba (solo laboratorio).

Todo se controla con variables de entorno para que Apache y NGINX publiquen
exactamente la misma aplicación con los mismos parámetros.
"""
from __future__ import annotations

import os
import secrets
from dataclasses import dataclass

BASELINE = "baseline"   # sin controles: sin bloqueo y sin registro de auditoría de la app
HARDENED = "hardened"   # con controles: bloqueo temporal + registro de auditoría


@dataclass(frozen=True)
class Config:
    server_label: str = "local"
    controls_mode: str = HARDENED
    max_failed_attempts: int = 3
    lock_seconds: int = 120
    db_path: str = "/var/lib/lab-app/users.db"
    audit_log_path: str = "/var/log/lab-app/auth.log"
    secret_key: str = ""
    trusted_proxy_hops: int = 0
    lab_user: str = "usuario.demo"
    lab_password: str = "LabDemo#2026"   # cuenta FICTICIA, solo para el laboratorio
    sweeper_interval: float = 1.0

    @property
    def controls_enabled(self) -> bool:
        return self.controls_mode == HARDENED

    @classmethod
    def from_env(cls) -> "Config":
        mode = os.getenv("CONTROLS_MODE", HARDENED).strip().lower()
        if mode not in (BASELINE, HARDENED):
            raise ValueError("CONTROLS_MODE debe ser 'baseline' o 'hardened'")
        return cls(
            server_label=os.getenv("SERVER_LABEL", "local"),
            controls_mode=mode,
            max_failed_attempts=int(os.getenv("MAX_FAILED_ATTEMPTS", "3")),
            lock_seconds=int(os.getenv("LOCK_SECONDS", "120")),
            db_path=os.getenv("DB_PATH", "/var/lib/lab-app/users.db"),
            audit_log_path=os.getenv("AUDIT_LOG_PATH", "/var/log/lab-app/auth.log"),
            secret_key=os.getenv("SECRET_KEY") or secrets.token_hex(32),
            trusted_proxy_hops=int(os.getenv("TRUSTED_PROXY_HOPS", "0")),
            lab_user=os.getenv("LAB_USER", "usuario.demo"),
            lab_password=os.getenv("LAB_PASSWORD", "LabDemo#2026"),
        )
