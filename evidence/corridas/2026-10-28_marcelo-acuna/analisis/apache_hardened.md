# Análisis de registros

## 1. Registro de auditoría de la aplicación (observado)

| Evento | Cantidad |
|---|---|
| LINK_VISIT | 1 |
| LOCKOUT_END | 3 |
| LOCKOUT_START | 3 |
| LOGIN_BLOCKED | 5 |
| LOGIN_FAILED | 9 |
| LOGIN_SUCCESS | 6 |

- Intentos de autenticación registrados: **20** (éxitos 6, fallidos 9, bloqueados 5)
- Usuarios ficticios involucrados: ['usuario.demo']
- IP de origen vistas por la app: ['172.18.0.1', '172.18.0.4']
- Rango de tiempo: 2026-10-27T23:13:53.407Z → 2026-10-27T23:31:43.230Z

### Secuencia (línea de tiempo)

| Hora (UTC) | Evento | Usuario | Resultado | IP | Fallos | Estado cuenta |
|---|---|---|---|---|---|---|
| 2026-10-27T23:13:53.407Z | LINK_VISIT |  | INFO | 172.18.0.1 |  |  |
| 2026-10-27T23:14:15.702Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.1 | 1 | unlocked |
| 2026-10-27T23:14:21.767Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.1 | 2 | unlocked |
| 2026-10-27T23:14:26.696Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.1 | 3 | locked |
| 2026-10-27T23:14:26.696Z | LOCKOUT_START | usuario.demo | INFO | 172.18.0.1 | 3 | locked |
| 2026-10-27T23:14:44.015Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.18.0.1 | 3 | locked |
| 2026-10-27T23:16:26.696Z | LOCKOUT_END | usuario.demo | INFO |  | 0 | unlocked |
| 2026-10-27T23:18:04.201Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.18.0.1 | 0 | unlocked |
| 2026-10-27T23:18:08.500Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.18.0.1 | 0 | unlocked |
| 2026-10-27T23:21:56.813Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.18.0.4 | 0 | unlocked |
| 2026-10-27T23:21:59.027Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 1 | unlocked |
| 2026-10-27T23:21:59.110Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 2 | unlocked |
| 2026-10-27T23:21:59.205Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:21:59.205Z | LOCKOUT_START | usuario.demo | INFO | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:21:59.372Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:21:59.412Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:23:59.205Z | LOCKOUT_END | usuario.demo | INFO |  | 0 | unlocked |
| 2026-10-27T23:24:02.438Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.18.0.4 | 0 | unlocked |
| 2026-10-27T23:29:39.830Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.18.0.4 | 0 | unlocked |
| 2026-10-27T23:29:39.895Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 1 | unlocked |
| 2026-10-27T23:29:39.986Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 2 | unlocked |
| 2026-10-27T23:29:40.079Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:29:40.079Z | LOCKOUT_START | usuario.demo | INFO | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:29:40.180Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:29:40.203Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:31:40.079Z | LOCKOUT_END | usuario.demo | INFO |  | 0 | unlocked |
| 2026-10-27T23:31:43.230Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.18.0.4 | 0 | unlocked |

- Bloqueos activados: **3**; finalizados: **3**

## 2. Registros de acceso de los servidores web (observado)

### apache

| Código HTTP | POST /login |
|---|---|
| 302 | 6 |
| 401 | 9 |
| 429 | 5 |

- IP de origen vistas por el servidor: ['172.18.0.1', '172.18.0.4']

## 3. Solicitudes capturadas por OWASP ZAP (observado)

| Código HTTP | POST /login |
|---|---|
| 302 | 2 |
| 401 | 3 |
| 429 | 2 |

## 4. Correlación de conteos

| Fuente | Intentos de login contados |
|---|---|
| Auditoría de la app | 20 |
| access.log apache | 20 |
| OWASP ZAP | 7 |

Si los números difieren, revise: pruebas previas en el mismo log, la precondición del script (1 login correcto previo), filtros de `--run-id` y que ZAP solo ve el tráfico que pasa por su proxy.

## 5. Observado vs. interpretado

- **Observado:** conteos, códigos HTTP, horas, IP y estado de bloqueo que aparecen en los archivos.
- **Interpretación (debe justificarse):** una IP por sí sola no demuestra que el intento venga de un atacante, ni si el origen es interno o externo. Cuando el tráfico pasa por ZAP, el servidor ve la IP de ZAP, no la del cliente.
- Las diferencias entre ZAP y los servidores se explican por el punto de captura (proxy vs. servidor vs. aplicación), no necesariamente por errores.
