# Guion de defensa: replicar el laboratorio de phishing desde cero

Repositorio: https://github.com/cmacuna7/proyecto-phishing-lab (rama `main`).

Todos los comandos van en **una sola ventana de CMD**, dentro de la carpeta del proyecto, salvo donde
se indica PowerShell. Cada paso tiene dos partes: **Qué ejecutar** y **Qué decir**.

**Orden de la demo:** 0 idea · 1 preparación · 2 baseline · 3 phishing · 4 ataque sin controles ·
5 hardened · 6 ataque con controles · 7 demo manual · 8 análisis · 9 ZAP con interfaz (opcional) ·
10 volver al modo normal · 11 comando único · 12 pruebas · 13 apagar · 14 si algo falla.

---

## 0. Idea en 20 segundos (para abrir la defensa)

> "Armamos un laboratorio aislado en Docker con una aplicación de inicio de sesión publicada por dos
> servidores web, Apache y NGINX, y una máquina de monitoreo con OWASP ZAP. Simulamos un mensaje de
> phishing con enlace y código QR que apunta solo al laboratorio. Corremos el mismo ataque de
> contraseñas dos veces, sin controles y con controles (bloqueo tras 3 fallos y registro de
> auditoría), y comparamos el riesgo antes y después."

---

## 1. Preparación (hacerla hoy, no el día de la defensa)

**Qué ejecutar**
```bat
cd "C:\ESPE\ING. SEGURIDAD DEL SOFTWARE\proyecto-phishing-lab"
git pull
docker version
docker compose version
python --version
```
La primera línea es la ruta de tu equipo; cámbiala si clonaste en otro lugar.

**Qué debe salir**
- `docker version` muestra *Client* y *Server*. Si falla, abre Docker Desktop y espera a que diga *Running*.
- Python 3.10 o superior.
- `git pull` trae los cambios del equipo.
- Comprueba que existan `phishing\qr_apache_navegador.png` y `docker-compose.zap-ui.yml` con el puerto **8180**. Si no están, alguien no los ha subido todavía.

**Qué decir:** "Clonamos el repositorio y usamos Docker Compose para que cualquier persona levante
exactamente el mismo laboratorio con un comando."

> **Consejo:** corre todo una vez completo hoy. La primera vez descarga imágenes y tarda varios
> minutos; el día de la defensa irá mucho más rápido.

### Nombre de la carpeta de la corrida (una sola vez)

Para no escribir la ruta en cada comando, guárdala en una variable de CMD:
```bat
set C=evidence/corridas/2026-10-28_marcelo-acuna_defensa
```
- Usa un nombre **nuevo**. Si la carpeta ya existe, los resultados se mezclan con los de una corrida anterior y la tabla comparativa sale con columnas repetidas.
- Escribe la ruta con `/` y **sin barra al final**. Una barra invertida al final (`...\resultados\`) crea dentro del contenedor una carpeta llamada `resultados\` que parece igual pero no lo es, y `compare_results.py` no encuentra esos archivos.
- En los comandos se usa como `%C%`. Para `xcopy` hace falta la ruta con `\`, que se escribe `%C:/=\%`: CMD cambia cada `/` por `\`.
- La variable, igual que `set CONTROLS_MODE`, solo existe en **esta** ventana de CMD. Si abres otra, vuelve a ejecutar los dos `set`.

---

## 2. Limpiar y levantar el laboratorio SIN controles (estado "antes")

**Qué ejecutar**
```bat
docker compose down
rmdir /s /q logs data
set CONTROLS_MODE=baseline
docker compose up -d --build --wait
docker compose ps
```

**Qué hace cada línea**
- `docker compose down`: apaga cualquier laboratorio anterior, incluido ZAP si quedó en modo gráfico.
- `rmdir /s /q logs data`: borra los registros y el estado (bloqueos y contadores) para empezar limpio. No toca `evidence`. Si dice *"El sistema no puede encontrar el archivo"*, es que ya estaba limpio: no pasa nada.
- `set CONTROLS_MODE=baseline`: la aplicación arranca sin controles (sin bloqueo y sin auditoría).
- `docker compose up -d --build --wait`: construye y levanta los 7 contenedores, y espera a que estén sanos.
- `docker compose ps`: lista los contenedores.

**Qué debe salir:** 7 contenedores *Up* y `zap` en *healthy*, que puede tardar cerca de 1 minuto. Son `app-apache`, `app-nginx`, `apache`, `nginx`, `zap`, `client1` y `client2`.

**Qué decir:** "Son siete contenedores en una red aislada llamada lab-net: dos aplicaciones iguales,
Apache, NGINX, ZAP y dos equipos de usuario. El equipo 1 navega a través de ZAP, así ZAP ve todo su
tráfico; el equipo 2 va directo, para comparar la dirección de origen. Ahora está en modo baseline:
la aplicación no tiene bloqueo ni auditoría. Todos los puertos están publicados solo en 127.0.0.1,
así que nadie fuera de este equipo puede entrar."

| Servicio | Dirección (desde el navegador de Windows) |
|---|---|
| Aplicación por Apache | http://127.0.0.1:8081 |
| Aplicación por NGINX | http://127.0.0.1:8082 |
| Enlace del QR simulado | http://127.0.0.1:8081/r/qr1 |
| Enlace del correo simulado | http://127.0.0.1:8081/r/mail1 |
| API de ZAP (modo normal) | http://127.0.0.1:8090 |

**Cuenta ficticia:** `usuario.demo` / `LabDemo#2026`.

---

## 3. Mostrar el mensaje de phishing y el código QR (la parte "social")

**Qué ejecutar:**
1. Abre `phishing\mensaje_simulado.md` y la imagen `phishing\qr_apache_navegador.png`.
2. Abre en el navegador http://127.0.0.1:8081/r/qr1.

`qr_apache.png` apunta a `http://apache/r/qr1`, un nombre que solo existe dentro de la red de Docker. Por eso, desde Windows se usa el QR `_navegador`, que apunta a `127.0.0.1:8081`. Un teléfono no puede abrir ninguno de los dos, porque `127.0.0.1` es el propio teléfono.

**Qué debe pasar:** el navegador termina en la pantalla de acceso con `?ref=afiche-qr` en la
dirección y la franja **SIMULACIÓN ACADÉMICA**. Con `/r/mail1` la dirección termina en `?ref=correo-simulado`.

**Qué decir:** "Este es el mensaje simulado: tiene urgencia, remitente genérico y un enlace corto que
oculta el destino. El código QR hace lo mismo desde un afiche. Los dos apuntan solo a nuestro
laboratorio: solo existen dos códigos fijos (qr1 y mail1) y no hay redirección abierta hacia otros
sitios. En modo con controles, cada visita queda registrada como LINK_VISIT con el nombre de la campaña."

---

## 4. Ejecutar el ataque SIN controles en Apache y en NGINX

**Qué ejecutar**
```bat
docker compose exec client1 python scripts/run_scenario.py --target apache --mode baseline --out-dir %C%/resultados
docker compose exec client1 python scripts/zap_export.py --baseurl http://apache --out %C%/zap/apache_baseline.csv
docker compose exec client1 python scripts/run_scenario.py --target nginx --mode baseline --out-dir %C%/resultados
docker compose exec client1 python scripts/zap_export.py --baseurl http://nginx --out %C%/zap/nginx_baseline.csv
xcopy logs "%C:/=\%\logs\baseline" /E /I /Y
del /s /q "%C:/=\%\logs\httpd.pid"
```

**Qué hace cada comando**
- `docker compose exec client1 ...`: ejecuta el comando dentro del equipo de usuario 1, que pasa por ZAP.
- `run_scenario.py` envía 7 solicitudes de inicio de sesión y compara el código HTTP obtenido con el esperado. Estas son:
  - 1 con la contraseña correcta, como precondición para dejar el contador en cero.
  - S1: 3 con la contraseña incorrecta.
  - S1b: un 4.º intento incorrecto.
  - S2 y S3: 2 con la correcta.
- `zap_export.py`: le pide a ZAP la lista de lo que capturó hacia ese servidor y la guarda en CSV, con usuario y contraseña enmascarados (`***`).
- `xcopy ... /E /I /Y`: copia `logs\` a la evidencia. `logs\` es la carpeta "en vivo" y se borra al reiniciar. Las opciones significan:
  - `/E`: incluye subcarpetas.
  - `/I`: crea la carpeta destino.
  - `/Y`: no pregunta antes de sobrescribir.
- `del ... httpd.pid`: borra un archivo técnico de Apache que no es evidencia.

**Qué debe salir en baseline (tabla al final de cada `run_scenario`)**

| Paso | Esperado | Significado |
|---|---|---|
| S1: 3 fallos | 401, 401, 401 | credencial incorrecta |
| S1b: 4.º fallo | 401 | no hay bloqueo |
| S2: correcta durante el "bloqueo" | 302 | entra: no hay control |
| S3: correcta después | 302 | entra |

Al final debe decir: `Resultado: TODO COINCIDE CON LO ESPERADO`. Cada `zap_export` dice
`8 mensajes exportados`: los 7 `POST /login` más un `GET` que ZAP anota al conectarse al servidor.
El análisis solo cuenta los `POST /login`.

**Qué decir:** "Sin controles, el atacante puede probar contraseñas sin límite: el cuarto intento
sigue dando 401 y no se bloquea nada. Esta es la línea base del riesgo de fuerza bruta. Además, la
aplicación no escribe auditoría: solo quedan los registros del servidor web y lo que vio ZAP, y en
ninguno de los dos se sabe si la cuenta estaba bloqueada."

---

## 5. Levantar el laboratorio CON controles (estado "después")

**Qué ejecutar**
```bat
docker compose down
rmdir /s /q logs data
set CONTROLS_MODE=hardened
docker compose up -d --build --wait
docker compose ps
```

**Qué decir:** "Mismo laboratorio y misma imagen de la aplicación; lo único que cambia es una
variable: ahora los controles están activos. Esto garantiza que la comparación sea justa."

**Controles activos:**
- Bloqueo de la cuenta durante 120 segundos tras 3 fallos consecutivos. Durante el bloqueo, incluso la contraseña correcta se rechaza.
- Registro de auditoría con fecha, usuario, resultado, dirección de origen y estado de bloqueo, sin contraseñas ni tokens.

---

## 6. Ejecutar el ataque CON controles en Apache y en NGINX

> Hazlo **antes** de la demostración manual. Así los registros de esta etapa solo tienen el
> ataque del script, y la auditoría, el servidor y ZAP cuentan lo mismo: 7 y 7 y 7. Las pruebas
> desde el navegador no pasan por ZAP, y si se mezclan, ZAP cuenta menos que la aplicación.

**Qué ejecutar**
```bat
docker compose exec client1 python scripts/run_scenario.py --target apache --mode hardened --out-dir %C%/resultados
docker compose exec client1 python scripts/zap_export.py --baseurl http://apache --out %C%/zap/apache_hardened.csv
docker compose exec client1 python scripts/run_scenario.py --target nginx --mode hardened --out-dir %C%/resultados
docker compose exec client1 python scripts/zap_export.py --baseurl http://nginx --out %C%/zap/nginx_hardened.csv
xcopy logs "%C:/=\%\logs\hardened" /E /I /Y
del /s /q "%C:/=\%\logs\httpd.pid"
```

Cada `run_scenario.py` tarda poco más de 2 minutos, porque en S3 espera a que termine el bloqueo.
Cuando imprime `[S3] esperando 123s a que termine el bloqueo...`, aprovecha para explicar la matriz
de riesgos o abrir `logs\app-apache\auth.log`.

Si imprime `[pre] cuenta bloqueada de una corrida anterior; esperando ...s`, la cuenta quedó
bloqueada por una prueba anterior. El script espera solo y luego sigue.

**Qué debe salir en hardened**

| Paso | Esperado | Significado |
|---|---|---|
| S1: 3 fallos | 401, 401, 401 | el tercero ya muestra el mensaje de bloqueo |
| S1b: 4.º fallo | 429 | bloqueado: ya ni se valida la contraseña |
| S2: correcta durante el bloqueo | 429 | la contraseña correcta también se rechaza |
| S3: correcta tras el bloqueo | 302 | entra otra vez |

**Qué decir:** "Con los controles el cuarto intento ya no llega a validar contraseñas: da 429, que
significa demasiadas solicitudes. Es el mismo resultado en Apache y en NGINX, lo que demuestra que el
control está en la aplicación y no depende del servidor web."

---

## 7. Demostración manual en el navegador (lo más convincente en vivo)

La evidencia ya está guardada, así que lo que hagas ahora no altera la comparación.

**Qué ejecutar:** abre http://127.0.0.1:8081/r/qr1 y haz, en orden:
1. Escribe `usuario.demo` con una contraseña incorrecta, 3 veces seguidas. La tercera muestra el mensaje de bloqueo.
2. Escribe la contraseña correcta (`LabDemo#2026`). Debe ser rechazada.
3. Espera 2 minutos y repite con la correcta: ahora entra.

Mientras esperas, abre `logs\app-apache\auth.log`. Cada línea es un evento: `LINK_VISIT`,
`LOGIN_FAILED`, `LOCKOUT_START`, `LOGIN_BLOCKED`, `LOCKOUT_END` y `LOGIN_SUCCESS`. Ninguna contiene contraseñas.

**Qué decir:** "A la tercera falla la cuenta se bloquea. Aunque ahora escriba la contraseña
correcta, el sistema la rechaza. Si fuera el dueño legítimo, tendría que esperar. Cuando pasan 120
segundos, el bloqueo termina solo. Esto frena la fuerza bruta, pero tiene un costo, que está en
nuestra matriz como R-07: alguien podría bloquear a propósito la cuenta de otra persona."

### Opcional: el equipo 2 (sin ZAP) para comparar la dirección de origen

```bat
docker compose exec client2 python scripts/run_scenario.py --target apache --mode hardened --out-dir /tmp/demo
```
`--out-dir /tmp/demo` deja el resultado dentro del contenedor y no lo mezcla con la evidencia.
Después abre `logs\apache\access.log`: las solicitudes del equipo 2 aparecen con **otra IP**. El
equipo 1 aparece con la IP de ZAP, porque es ZAP quien se conecta al servidor. El navegador de
Windows aparece con la IP de la puerta de enlace de Docker, que termina en `.1`.

Para saber qué IP tiene cada contenedor:
```bat
docker network inspect seg-phishing-lab_lab-net --format "{{range .Containers}}{{.Name}} {{.IPv4Address}}{{println}}{{end}}"
```

---

## 8. Análisis de los registros (reconstruir lo que pasó)

Estos comandos usan el Python del equipo, no el del contenedor. Cada uno debe ir en **una sola
línea**: si se parte al pegar, sale `expected one argument` o `"evidence" no se reconoce como un comando`.

**Qué ejecutar**
```bat
python scripts/analyze_logs.py --access apache=%C%/logs/baseline/apache/access.log --zap-csv %C%/zap/apache_baseline.csv --out %C%/analisis/apache_baseline.md
python scripts/analyze_logs.py --access nginx=%C%/logs/baseline/nginx/access.log --zap-csv %C%/zap/nginx_baseline.csv --out %C%/analisis/nginx_baseline.md
python scripts/analyze_logs.py --audit %C%/logs/hardened/app-apache/auth.log --access apache=%C%/logs/hardened/apache/access.log --zap-csv %C%/zap/apache_hardened.csv --out %C%/analisis/apache_hardened.md
python scripts/analyze_logs.py --audit %C%/logs/hardened/app-nginx/auth.log --access nginx=%C%/logs/hardened/nginx/access.log --zap-csv %C%/zap/nginx_hardened.csv --out %C%/analisis/nginx_hardened.md
python scripts/compare_results.py --results "%C%/resultados/*.json" --out %C%/analisis/comparacion.md
python scripts/compare_results.py
```

**Qué hace cada comando**
- `analyze_logs.py` cruza las tres fuentes de un servidor y escribe un informe `.md`:
  - `--audit`: lo que registró la aplicación. En baseline no se usa, porque esa etapa no tiene auditoría.
  - `--access`: lo que registró el servidor web.
  - `--zap-csv`: lo que capturó ZAP.
- El primer `compare_results.py` arma la tabla antes/después de **tu** corrida, con 4 columnas: apache y nginx, en baseline y en hardened.
- El segundo, sin argumentos, actualiza `evidence/corridas/comparacion.md`, que tiene todas las corridas del equipo lado a lado.

**Qué debe salir**
- **Baseline:** el servidor y ZAP cuentan 7 intentos cada uno (302 = 3, 401 = 4). No hay sección de auditoría.
- **Hardened:** la auditoría, el servidor y ZAP cuentan **7** cada uno (302 = 2, 401 = 3, 429 = 2). Además:
  - La línea de tiempo muestra `LOCKOUT_START` en el tercer fallo.
  - Muestra `LOCKOUT_END` exactamente 120 s después.
  - Dice `Bloqueos activados: 1; finalizados: 1`.
- **Comparación:**
  - El riesgo de fuerza bruta (R-01) pasa de 12 (Alto) a 9 (Moderado).
  - El 4.º fallo pasa de 401 a 429.
  - "Todos los pasos coinciden" dice **Sí** en las 4 columnas.

**Qué decir:** "El análisis cruza tres fuentes independientes: la auditoría de la aplicación, el
registro de acceso del servidor web y lo que capturó ZAP. En hardened las tres cuentan 7 intentos y
los códigos 401, 429 y 302 coinciden. La línea de tiempo muestra que el bloqueo empieza en el tercer
fallo y termina exactamente 120 segundos después. Lo observado son hechos de los archivos. Lo
interpretado, por ejemplo que la IP que ve el servidor es la de ZAP, lo verificamos aparte con
`docker network inspect`."

> Si un conteo no coincide, normalmente hay más tráfico en el registro que solo el script: pruebas
> del navegador (IP terminada en `.1`, no pasan por ZAP) o el escenario corrido dos veces. No es
> un error del control; se explica por el punto de captura.

---

## 9. Opcional: ver ZAP con interfaz gráfica en el navegador (para capturas)

En el modo normal, ZAP corre sin interfaz (*daemon*), solo con su API. Para ver el historial de
solicitudes en pantalla, se arranca con el archivo extra `docker-compose.zap-ui.yml`. Hazlo
**después** del paso 8: al reiniciar ZAP se pierde lo que había capturado, pero eso ya quedó exportado.

**Qué ejecutar**
```bat
docker compose down
rmdir /s /q logs data
set CONTROLS_MODE=hardened
docker compose -f docker-compose.yml -f docker-compose.zap-ui.yml up -d --build
```
- No uses `--wait` aquí. En modo gráfico ZAP no arranca hasta que se abre su página, así que `--wait` se queda esperando y falla.
- Abre **http://127.0.0.1:8180/zap/**, con `/zap/` al final, y espera cerca de 1 minuto a que aparezca la ventana de ZAP.
  - Si abres solo `http://127.0.0.1:8180`, sale un **inicio de sesión de Webswing**. Esa es la consola de administración del visor y **no hay usuario ni contraseña**: no es ZAP.
  - Si ZAP pregunta si quieres guardar la sesión, elige *no persistir*.
- Se usa el puerto 8180 y no el 8080 porque en muchos equipos el 8080 ya está ocupado, por ejemplo por AppServ.

Con ZAP abierto en el navegador, genera tráfico:
```bat
docker compose exec client1 python scripts/run_scenario.py --target apache --mode hardened --out-dir /tmp/zap-ui
```
`--out-dir /tmp/zap-ui` deja ese resultado dentro del contenedor, porque esta corrida es solo para
las capturas y no debe mezclarse con la evidencia.

**Qué mostrar en ZAP**
- Pestaña **Historial** (abajo): las solicitudes `POST http://apache/login` con códigos 302, 401, 401, 401, 429, 429 y 302.
- Clic en una solicitud **429**: en *Respuesta* aparece `Retry-After: 120` y el mensaje de bloqueo.
- **Tapa o recorta la contraseña antes de guardar la captura.** En la pestaña *Solicitud*, ZAP muestra el cuerpo del formulario sin enmascarar (`password=LabDemo%232026`), y la regla del proyecto es no dejar contraseñas en la evidencia.

**Qué decir:** "Esta es la máquina de monitoreo. ZAP es un proxy: el equipo 1 le envía todo su
tráfico y él lo reenvía al servidor, así que vemos cada solicitud y cada respuesta. Aquí están los
tres 401 y luego los 429 del bloqueo."

> En modo gráfico **no se puede exportar** con `zap_export.py`, porque la API de ZAP pide una clave.
> Para exportar, vuelve al modo normal (paso 10).

---

## 10. Salir del modo gráfico y volver al modo normal (para exportar)

**Qué ejecutar**
```bat
docker compose down
```
Esto apaga todo, también ZAP en modo gráfico. Ya puedes cerrar la pestaña de `:8180/zap/`.

Para volver a trabajar en modo normal, levanta **sin** el `-f docker-compose.zap-ui.yml`:
```bat
rmdir /s /q logs data
set CONTROLS_MODE=hardened
docker compose up -d --build --wait
docker compose ps
```
`zap` vuelve a *healthy* en el puerto 8090 con la API abierta. Desde aquí `zap_export.py` vuelve a
funcionar: repite los pasos 4 a 8 o usa el comando único del paso 11.

---

## 11. Alternativa: todo en un comando

Para replicar el experimento completo (pasos 2 a 8) y guardar la evidencia, en **PowerShell**
dentro de la carpeta:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\corrida.ps1 -Persona marcelo-acuna
```
Tarda unos 6 a 8 minutos. El script hace todo lo de los pasos 2 a 8:
- Corre baseline y hardened, exporta ZAP y copia los registros.
- Genera el análisis en `evidence\corridas\<fecha>_marcelo-acuna\`.
- Actualiza `evidence\corridas\comparacion.md`.
- Si la carpeta ya existe, crea `_2`, `_3`, etc., y nunca sobrescribe.
- Siempre levanta ZAP en modo normal, aunque antes estuviera en modo gráfico.

Para regenerar solo el análisis de una corrida ya hecha:
```powershell
.\scripts\corrida.ps1 -Carpeta evidence\corridas\<carpeta> -SoloAnalizar
```

**Recomendación:** para la defensa usa los pasos manuales, así puedes explicar cada uno, y deja el
comando único como respaldo si el tiempo aprieta.

---

## 12. Pruebas unitarias (opcional, sin Docker)

```bat
pip install -r app/requirements.txt pytest
cd app
python -m pytest -q
cd ..
```
Debe decir `16 passed`.

**Qué decir:** "Las pruebas unitarias verifican la lógica del bloqueo y que el registro de auditoría
nunca guarde secretos."

---

## 13. Apagar

```bat
docker compose down
```

Si vas a subir tu corrida:
```bat
git add evidence/corridas
git commit -m "Corrida de defensa"
git push
```

---

## 14. Si algo falla en vivo

| Síntoma | Qué hacer |
|---|---|
| `docker version` falla | Abrir Docker Desktop y esperar a que diga *Running* |
| `zap` no llega a *healthy* | Esperar 1 a 2 minutos y repetir `docker compose ps` |
| Conexión rechazada hacia ZAP | El script espera hasta 3 minutos; si no, `docker compose ps` y esperar |
| Puerto 8081 u 8082 ocupado | Cerrar el programa que lo usa o `docker compose down` |
| `ports are not available ... 8080` o `8180` | Otro programa usa ese puerto. El modo gráfico usa 8180; si también está ocupado, cambia el `8180` en `docker-compose.zap-ui.yml` |
| Sale un inicio de sesión al abrir ZAP gráfico | Abriste la raíz `:8180`. Usa **http://127.0.0.1:8180/zap/**; no hay usuario ni contraseña |
| `up --wait` falla en modo gráfico | Normal: en modo gráfico se levanta sin `--wait` y luego se abre `/zap/` |
| `zap_export.py` falla tras usar el modo gráfico | ZAP sigue en modo gráfico. Ejecuta el paso 10 |
| `set` no tiene efecto | Estás en otra ventana de CMD: el modo y `%C%` se fijan en la misma ventana que levanta Docker |
| Quedaron bloqueos viejos | `docker compose down`, `rmdir /s /q logs data` y volver a levantar |
| `expected one argument` o `"evidence" no se reconoce` | El comando se partió en dos líneas al pegarlo: pégalo en una sola |
| La comparación sale sin una columna o con columnas repetidas | Revisa `%C%\resultados`: debe haber exactamente 4 `.json`. Si hay otra carpeta `resultados` "repetida", es por una `\` al final de `--out-dir` |
| Los conteos de ZAP y de la app no coinciden | Hay pruebas del navegador o corridas repetidas en el mismo registro (ver la nota del paso 8) |
| Cambios de Git no se aplican | `git status`, luego `git pull` |
| El QR no abre en el navegador | Usa `qr_apache_navegador.png` o http://127.0.0.1:8081/r/qr1; `http://apache/...` solo existe dentro de Docker |
