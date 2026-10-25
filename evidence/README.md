# Evidencia

| Carpeta | Qué guardar |
|---|---|
| `capturas/` | Figuras del informe (`figNN_*.png`, misma numeración que el PDF) y los diagramas de red y UML. Falta una captura de ZAP con solicitud/respuesta. |
| `zap/` | Exportaciones CSV de ZAP (`apache_<modo>.csv`, `nginx_<modo>.csv`). |
| `logs/` | Copia de `logs/` de cada corrida: `baseline/` (sin controles: no hay `auth.log`, es lo esperado) y `hardened/`. |
| `resultados/` | JSON/CSV de `scripts/run_scenario.py`. `previas/` guarda corridas anteriores que no entran en la comparación. |
| `analisis/` | Informes Markdown de `scripts/analyze_logs.py`. |

## Nomenclatura
`AAAA-MM-DD_<servidor>_<modo>_<descripcion>.<ext>` — p. ej. `2026-10-25_apache_hardened_bloqueo.png`.

## Enmascarado obligatorio
- Cubrir contraseñas, tokens y cookies de sesión en capturas.
- No subir archivos `.har` ni sesiones de ZAP (están en `.gitignore`).
- Solo usuario ficticio e IPs del laboratorio.
