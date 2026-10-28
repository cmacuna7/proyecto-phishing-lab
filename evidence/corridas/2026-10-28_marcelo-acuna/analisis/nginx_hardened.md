# Análisis de registros

## 1. Registro de auditoría de la aplicación (observado)

| Evento | Cantidad |
|---|---|
| LOCKOUT_END | 2 |
| LOCKOUT_START | 2 |
| LOGIN_BLOCKED | 5 |
| LOGIN_FAILED | 6 |
| LOGIN_SUCCESS | 3 |

- Intentos de autenticación registrados: **14** (éxitos 3, fallidos 6, bloqueados 5)
- Usuarios ficticios involucrados: ['usuario.demo']
- IP de origen vistas por la app: ['172.18.0.4']
- Rango de tiempo: 2026-10-27T23:34:41.631Z → 2026-10-27T23:38:48.185Z

### Secuencia (línea de tiempo)

| Hora (UTC) | Evento | Usuario | Resultado | IP | Fallos | Estado cuenta |
|---|---|---|---|---|---|---|
| 2026-10-27T23:34:41.631Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.18.0.4 | 0 | unlocked |
| 2026-10-27T23:34:41.720Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 1 | unlocked |
| 2026-10-27T23:34:41.804Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 2 | unlocked |
| 2026-10-27T23:34:41.916Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:34:41.916Z | LOCKOUT_START | usuario.demo | INFO | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:34:42.057Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:34:42.078Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:35:05.405Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:36:41.916Z | LOCKOUT_END | usuario.demo | INFO |  | 0 | unlocked |
| 2026-10-27T23:36:44.419Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.18.0.4 | 0 | unlocked |
| 2026-10-27T23:36:44.928Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 1 | unlocked |
| 2026-10-27T23:36:44.995Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 2 | unlocked |
| 2026-10-27T23:36:45.064Z | LOGIN_FAILED | usuario.demo | FAILED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:36:45.064Z | LOCKOUT_START | usuario.demo | INFO | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:36:45.137Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:36:45.155Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.18.0.4 | 3 | locked |
| 2026-10-27T23:38:45.064Z | LOCKOUT_END | usuario.demo | INFO |  | 0 | unlocked |
| 2026-10-27T23:38:48.185Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.18.0.4 | 0 | unlocked |

- Bloqueos activados: **2**; finalizados: **2**

## 2. Registros de acceso de los servidores web (observado)

### nginx

| Código HTTP | POST /login |
|---|---|
| 302 | 3 |
| 401 | 6 |
| 429 | 5 |

- IP de origen vistas por el servidor: ['172.18.0.4']

## 3. Solicitudes capturadas por OWASP ZAP (observado)

| Código HTTP | POST /login |
|---|---|
| 302 | 3 |
| 401 | 6 |
| 429 | 5 |

## 4. Correlación de conteos

| Fuente | Intentos de login contados |
|---|---|
| Auditoría de la app | 14 |
| access.log nginx | 14 |
| OWASP ZAP | 14 |

Si los números difieren, revise: pruebas previas en el mismo log, la precondición del script (1 login correcto previo), filtros de `--run-id` y que ZAP solo ve el tráfico que pasa por su proxy.

## 5. Observado vs. interpretado

- **Observado:** conteos, códigos HTTP, horas, IP y estado de bloqueo que aparecen en los archivos.
- **Interpretación (debe justificarse):** una IP por sí sola no demuestra que el intento venga de un atacante, ni si el origen es interno o externo. Cuando el tráfico pasa por ZAP, el servidor ve la IP de ZAP, no la del cliente.
- Las diferencias entre ZAP y los servidores se explican por el punto de captura (proxy vs. servidor vs. aplicación), no necesariamente por errores.
