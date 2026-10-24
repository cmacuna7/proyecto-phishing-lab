# Proyecto: Laboratorio de simulación de phishing, monitoreo y reducción de riesgo

Proyecto de la Unidad 1 de *Ingeniería de Seguridad del Software* (ESPE). Todo el contenido es **académico**: cuentas ficticias, red aislada y enlaces/QR que apuntan **solo** al laboratorio.

## Qué contiene

| Carpeta | Contenido |
|---|---|
| `app/` | Aplicación de prueba (Flask) con login, bloqueo temporal tras 3 fallos y registro de auditoría. Modos `baseline` (sin controles) y `hardened` (con controles). Incluye 16 pruebas (`pytest`). |
| `servers/apache`, `servers/nginx` | Configuración de Apache httpd 2.4 y NGINX como proxy inverso de la misma app, con el mismo formato de log. |
| `docker-compose.yml` | Laboratorio completo: 2 apps, Apache, NGINX, OWASP ZAP (proxy), `client1` (pasa por ZAP) y `client2` (directo). |
| `scripts/` | `run_scenario.py` (escenarios S1–S3), `analyze_logs.py`, `compare_results.py`, `zap_export.py`, `make_qr.py`. |
| `phishing/` | Mensaje simulado y códigos QR (solo hacia el laboratorio). |
| `matrices/` | `matriz_riesgos.xlsx` (hojas Inicial, Residual, Escala), riesgos R-01 a R-07. |
| `docs/` | Plan de trabajo, laboratorio, diseño (UML), investigación de casos reales y correcciones del informe. |
| `evidence/` | Capturas, logs curados, exportaciones de ZAP, resultados y análisis. |

## Inicio rápido

```bash
cp .env.example .env        # opcional
make baseline               # estado "antes" (sin controles)
make scenario-apache MODE=baseline
make scenario-nginx  MODE=baseline
make hardened               # estado "después" (bloqueo + auditoría)
make scenario-apache && make scenario-nginx
make analyze && make compare
make test                   # pruebas unitarias (no requiere Docker)
```

`make compare` lee los registros de `logs/`. Si ya se borraron, use los copiados en la evidencia:
`python scripts/compare_results.py --logs-dir evidence/logs/hardened`.

Accesos: Apache `http://127.0.0.1:8081`, NGINX `http://127.0.0.1:8082`, API de ZAP `127.0.0.1:8090`.
Cuenta ficticia: `usuario.demo` / `LabDemo#2026`.

## Reglas de seguridad (obligatorias)

1. Ninguna cuenta, correo, dominio o persona real. Solo la cuenta ficticia.
2. El enlace/QR apunta únicamente a `apache` o `nginx` del laboratorio (`make_qr.py` rechaza otros destinos).
3. No se registran contraseñas ni tokens en logs, capturas ni scripts (campos enmascarados).
4. ZAP está enlazado a `127.0.0.1` y sin clave de API: solo para uso local en el laboratorio.
5. No se sube evidencia con secretos (ver `.gitignore` y `evidence/README.md`).

## Requisito → entregable

| Requisito del PDF | Dónde está |
|---|---|
| Laboratorio aislado (2 usuarios, Apache, NGINX, monitoreo con ZAP) | `docker-compose.yml`, `docs/laboratorio.md` |
| Misma app con login y cuenta ficticia en ambos servidores | `app/`, `servers/` |
| Mensaje simulado con enlace/QR hacia el laboratorio | `phishing/` |
| Captura HTTP con ZAP | `scripts/zap_export.py`, `evidence/zap/` |
| Registro de autenticación (fecha, usuario, resultado, IP, bloqueo; sin secretos) | `app/labapp/audit.py` |
| Bloqueo temporal tras 3 fallos, aun con contraseña correcta, con inicio/fin registrados | `app/labapp/auth.py`, `app/tests/` |
| Matrices inicial y residual con la misma escala | `matrices/matriz_riesgos.xlsx` |
| Mapeo NIST CSF 2.0 e ISO/IEC 27005 | matriz (hoja Residual), `docs/informe/informe.md` |
| Comparación antes/después y Apache vs NGINX | `scripts/compare_results.py` |
| Informe técnico, evidencia y demo | Informe en Word (fuera del repositorio), `docs/informe/correcciones-informe.md`, `evidence/` |

## Estado y limitaciones

- **Verificado (22/10/2026):** laboratorio completo con Docker Compose, captura con ZAP y `zap_export.py`, escenario S1–S3 en Apache y NGINX en ambos modos, y correlación de 7 intentos entre auditoría, `access.log` y ZAP (`evidence/`). Pruebas unitarias: 16/16.
- El laboratorio usa **HTTP sin TLS** (limitación documentada; riesgo R-06).
- Los valores de las matrices son valoraciones del equipo; cada uno está marcado como OBSERVADO o JUICIO.
- Las pruebas manuales desde el navegador (enlace `/r/qr1`, usuario desconocido, bloqueo de las 18:19) solo están en la captura del `auth.log`; los logs de `evidence/logs/` se copiaron antes.
- Los casos reales de phishing están en `docs/investigacion/casos-phishing.md`.
