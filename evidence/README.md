# Evidencia

| Carpeta | Qué guardar |
|---|---|
| `capturas/` | Capturas de pantalla (PNG) de configuración, mensaje simulado, login, bloqueo, ZAP. |
| `zap/` | Exportaciones CSV de ZAP (`apache_<modo>.csv`, `nginx_<modo>.csv`). |
| `logs/` | Extractos curados de `auth.log` y `access.log` (no los logs completos). |
| `resultados/` | JSON/CSV de `scripts/run_scenario.py`. |
| `analisis/` | Informes Markdown de `scripts/analyze_logs.py`. |

## Nomenclatura
`AAAA-MM-DD_<servidor>_<modo>_<descripcion>.<ext>` — p. ej. `2026-10-25_apache_hardened_bloqueo.png`.

## Enmascarado obligatorio
- Cubrir contraseñas, tokens y cookies de sesión en capturas.
- No subir archivos `.har` ni sesiones de ZAP (están en `.gitignore`).
- Solo usuario ficticio e IPs del laboratorio.
