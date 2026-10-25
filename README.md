# Laboratorio de simulación de phishing, monitoreo y reducción de riesgos

Proyecto de la Unidad 1 de *Ingeniería de Seguridad del Software* (ESPE).
Todo es **académico**: cuenta ficticia, red aislada en Docker y enlaces/QR que apuntan **solo** al laboratorio.

**¿Qué hace?** Simula un phishing (mensaje con enlace corto o QR) hacia una aplicación de login publicada detrás de **Apache** y de **NGINX**, captura el tráfico con **OWASP ZAP**, registra cada intento de autenticación y **bloquea la cuenta 120 s tras 3 fallos consecutivos**. Se corre dos veces —sin controles (`baseline`) y con controles (`hardened`)— para comparar el riesgo antes y después.

---

## ¿Por dónde empiezo?

| Si quieres… | Ve a |
|---|---|
| Ejecutar el laboratorio | [Cómo ejecutarlo](#cómo-ejecutarlo-paso-a-paso) (abajo) |
| Ver qué pide la actividad y si se cumple | [`docs/cumplimiento.md`](docs/cumplimiento.md) |
| Leer el informe técnico entregado | [`docs/informe/informe-tecnico.pdf`](docs/informe/informe-tecnico.pdf) |
| Leer el enunciado del proyecto | [`docs/enunciado-proyecto.pdf`](docs/enunciado-proyecto.pdf) |
| Ver las capturas y resultados | [`evidence/`](evidence/README.md) |
| Ver las matrices de riesgo | [`matrices/matriz_riesgos.xlsx`](matrices/matriz_riesgos.xlsx) |
| Preparar la exposición / demo | [`docs/guia-explicacion.md`](docs/guia-explicacion.md) y [`docs/laboratorio.md`](docs/laboratorio.md) |

---

## Cómo ejecutarlo (paso a paso)

### Requisitos
- **Docker Desktop** encendido (incluye Docker Compose).
- **Python 3.10+** en el equipo, solo para analizar resultados y correr pruebas.
- Opcional: `make` (Linux/WSL/Git Bash). En Windows **no hace falta**: abajo están los comandos para PowerShell.

Todos los comandos se ejecutan en **PowerShell, dentro de la carpeta del proyecto**.

### 1. Levantar el laboratorio
```powershell
docker compose up -d --build     # la primera vez tarda unos minutos (descarga imágenes)
docker compose ps                # deben aparecer 7 contenedores; zap en "healthy" (~1 min)
```
Abre en el navegador:

| Servicio | URL |
|---|---|
| App publicada por **Apache** | http://127.0.0.1:8081 |
| App publicada por **NGINX** | http://127.0.0.1:8082 |
| Enlace del QR simulado | http://127.0.0.1:8081/r/qr1 |
| API de OWASP ZAP | http://127.0.0.1:8090 |

**Cuenta ficticia:** `usuario.demo` / `LabDemo#2026`

> Por defecto arranca en modo `hardened` (con controles). Prueba 3 contraseñas incorrectas y verás el mensaje de bloqueo; durante 120 s ni la contraseña correcta funciona.

### 2. Corrida "antes" (sin controles)
```powershell
docker compose down; Remove-Item -Recurse -Force logs, data -ErrorAction SilentlyContinue
$env:CONTROLS_MODE = "baseline"; docker compose up -d --build
docker compose exec client1 python scripts/run_scenario.py --target apache --mode baseline
docker compose exec client1 python scripts/run_scenario.py --target nginx  --mode baseline
docker compose exec client1 python scripts/zap_export.py --baseurl http://apache --out evidence/zap/apache_baseline.csv
docker compose exec client1 python scripts/zap_export.py --baseurl http://nginx  --out evidence/zap/nginx_baseline.csv
Remove-Item -Recurse -Force evidence\logs\baseline; Copy-Item -Recurse logs evidence\logs\baseline   # reemplaza la evidencia de logs
```

### 3. Corrida "después" (con controles)
```powershell
docker compose down; Remove-Item -Recurse -Force logs, data -ErrorAction SilentlyContinue
$env:CONTROLS_MODE = "hardened"; docker compose up -d --build
docker compose exec client1 python scripts/run_scenario.py --target apache --mode hardened   # ~2 min: espera el fin del bloqueo
docker compose exec client1 python scripts/run_scenario.py --target nginx  --mode hardened
docker compose exec client1 python scripts/zap_export.py --baseurl http://apache --out evidence/zap/apache_hardened.csv
docker compose exec client1 python scripts/zap_export.py --baseurl http://nginx  --out evidence/zap/nginx_hardened.csv
Remove-Item -Recurse -Force evidence\logs\hardened; Copy-Item -Recurse logs evidence\logs\hardened   # reemplaza la evidencia de logs
```

El escenario (`scripts/run_scenario.py`) ejecuta: **S1** 3 fallos seguidos → **S1b** 4.º fallo (con controles: 429) → **S2** contraseña correcta durante el bloqueo (con controles: 429) → **S3** contraseña correcta al terminar el bloqueo (302). Guarda el resultado en `evidence/resultados/`.

### 4. Analizar y comparar (en el equipo, no en Docker)
```powershell
python scripts/analyze_logs.py --audit evidence/logs/hardened/app-apache/auth.log --access apache=evidence/logs/hardened/apache/access.log --zap-csv evidence/zap/apache_hardened.csv --out evidence/analisis/apache_hardened.md
python scripts/analyze_logs.py --audit evidence/logs/hardened/app-nginx/auth.log  --access nginx=evidence/logs/hardened/nginx/access.log  --zap-csv evidence/zap/nginx_hardened.csv  --out evidence/analisis/nginx_hardened.md
python scripts/compare_results.py --logs-dir evidence/logs/hardened      # genera evidence/analisis/comparacion.md
```
(Para `baseline`, cambia `hardened` por `baseline` en las dos primeras líneas.)
`compare_results.py` lee **todos** los `.json` de `evidence/resultados/`: si repites corridas, mueve las viejas a `evidence/resultados/previas/`.

### 5. Pruebas unitarias (sin Docker)
```powershell
pip install -r app/requirements.txt pytest
cd app; python -m pytest -q; cd ..        # 16 pruebas
```

### 6. Apagar
```powershell
docker compose down
```

**Con `make`** (Linux/WSL): `make baseline`, `make scenario-apache MODE=baseline`, `make hardened`, `make scenario-apache`, `make zap-export`, `make analyze`, `make compare`, `make test`. Ver [`Makefile`](Makefile).

**ZAP con interfaz gráfica** (para capturas de pantalla): `docker compose -f docker-compose.yml -f docker-compose.zap-ui.yml up -d zap` y abre http://127.0.0.1:8080/zap.

---

## Estructura del repositorio

```
├── app/                  Aplicación de prueba (Flask): login, bloqueo, auditoría + 16 pruebas
│   └── labapp/           auth.py (bloqueo) · audit.py (registro sin secretos) · config.py
├── servers/              Configuración de Apache (httpd.conf) y NGINX (nginx.conf) como proxy inverso
├── clients/              Imagen de los 2 "equipos de usuario" (client1 pasa por ZAP, client2 directo)
├── scripts/              run_scenario · zap_export · analyze_logs · compare_results · make_qr
├── phishing/             Mensaje simulado y códigos QR (solo hacia el laboratorio)
├── matrices/             matriz_riesgos.xlsx (hojas Inicial, Residual, Escala)
├── docs/                 Enunciado, informe, cumplimiento, diseño UML, laboratorio, casos reales
├── evidence/             Capturas, logs, exportaciones de ZAP, resultados y análisis
├── tools/                build_matriz_xlsx.py (plantilla de la matriz; NO ejecutar: sobrescribe el Excel)
├── docker-compose.yml    Laboratorio completo (7 contenedores en la red aislada lab-net)
└── Makefile              Atajos para Linux/WSL
```

**Carpetas que aparecen vacías:** `logs/` y `data/` se crean al levantar Docker y **no se suben a git** (`.gitignore`): son los registros y el estado en vivo. `logs/app-apache/` y `logs/app-nginx/` quedan vacías hasta que alguien intenta iniciar sesión en modo `hardened`; en `baseline` la app no escribe auditoría (es lo que se quiere demostrar). Los registros que sí sirven como evidencia se copian a `evidence/logs/`.

---

## Reglas de seguridad (obligatorias)

1. Ninguna cuenta, correo, dominio o persona real. Solo la cuenta ficticia.
2. El enlace/QR apunta únicamente a `apache` o `nginx` del laboratorio (`make_qr.py` rechaza otros destinos).
3. No se registran contraseñas ni tokens en logs, capturas ni scripts (campos enmascarados).
4. ZAP está enlazado a `127.0.0.1` y sin clave de API: solo para uso local.
5. No subir evidencia con secretos (ver `.gitignore` y [`evidence/README.md`](evidence/README.md)).

## Limitaciones conocidas

- HTTP sin TLS (riesgo R-06, documentado).
- Los "equipos" son contenedores Docker, no máquinas virtuales (ver [`docs/laboratorio.md`](docs/laboratorio.md) si el docente exige VM).
- Los valores de las matrices son valoraciones del equipo, marcadas como OBSERVADO o JUICIO.
- Estado de cumplimiento y pendientes del informe: [`docs/cumplimiento.md`](docs/cumplimiento.md).
