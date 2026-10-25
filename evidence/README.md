# Evidencia

| Carpeta | Qué contiene |
|---|---|
| `capturas/` | Figuras del informe (`figNN_*.png`, misma numeración que el PDF) y los diagramas de red y UML. Falta una captura de ZAP con solicitud/respuesta. |
| `corridas/` | Una carpeta por cada ejecución del laboratorio, `<AAAA-MM-DD>_<persona>`, creada por `scripts/corrida.ps1`. Nunca se sobrescriben. |
| `corridas/comparacion.md` | Todas las corridas lado a lado (columna = servidor · modo · corrida). |

## Contenido de cada corrida
| Subcarpeta | Qué guarda |
|---|---|
| `resultados/` | JSON/CSV de `scripts/run_scenario.py` (código HTTP esperado vs obtenido en S1–S3). |
| `zap/` | Exportaciones CSV de ZAP (`<servidor>_<modo>.csv`, formulario enmascarado). |
| `logs/baseline/`, `logs/hardened/` | Copia de `logs/`: `access.log` de Apache/NGINX y `auth.log` de la app. En `baseline` no hay `auth.log`: sin controles la app no audita (es lo esperado). |
| `analisis/` | `analyze_logs.py` (secuencia de intentos, correlación auditoría–servidor–ZAP) y `comparacion.md` de la corrida. |

## Corridas registradas
| Corrida | Quién | Nota |
|---|---|---|
| `2026-10-22_marcelo-acuna` | Marcelo Acuña | Es la que usa el informe. `resultados/previas/` tiene un primer intento de Apache hardened que no entra en la comparación. |
| `2026-10-25_zaith-manangon` | Zaith Manangón | Repetición completa; mismos resultados. |

## Enmascarado obligatorio
- Cubrir contraseñas, tokens y cookies de sesión en capturas.
- No subir archivos `.har` ni sesiones de ZAP (están en `.gitignore`).
- Solo usuario ficticio e IPs del laboratorio.
