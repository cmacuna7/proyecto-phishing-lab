# Análisis de registros

## 1. Registro de auditoría de la aplicación (observado)

| Evento | Cantidad |
|---|---|
| LOCKOUT_END | 1 |
| LOCKOUT_START | 1 |
| LOGIN_BLOCKED | 2 |
| LOGIN_FAILED | 3 |
| LOGIN_SUCCESS | 2 |

- Intentos de autenticación registrados: **7** (éxitos 2, fallidos 3, bloqueados 2)
- Usuarios ficticios involucrados: ['usuario.demo']
- IP de origen vistas por la app: ['172.22.0.3']
- Rango de tiempo: 2026-10-22T18:05:26.260Z → 2026-10-22T18:07:29.730Z

### Secuencia (línea de tiempo)

| Hora (UTC) | Evento | Usuario | Resultado | IP | Fallos | Estado cuenta |
|---|---|---|---|---|---|---|
| 2026-10-22T18:05:26.260Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.22.0.3 | 0 | unlocked |
| 2026-10-22T18:05:26.349Z | LOGIN_FAILED | usuario.demo | FAILED | 172.22.0.3 | 1 | unlocked |
| 2026-10-22T18:05:26.438Z | LOGIN_FAILED | usuario.demo | FAILED | 172.22.0.3 | 2 | unlocked |
| 2026-10-22T18:05:26.536Z | LOGIN_FAILED | usuario.demo | FAILED | 172.22.0.3 | 3 | locked |
| 2026-10-22T18:05:26.536Z | LOCKOUT_START | usuario.demo | INFO | 172.22.0.3 | 3 | locked |
| 2026-10-22T18:05:26.643Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.22.0.3 | 3 | locked |
| 2026-10-22T18:05:26.688Z | LOGIN_BLOCKED | usuario.demo | BLOCKED | 172.22.0.3 | 3 | locked |
| 2026-10-22T18:07:26.536Z | LOCKOUT_END | usuario.demo | INFO |  | 0 | unlocked |
| 2026-10-22T18:07:29.730Z | LOGIN_SUCCESS | usuario.demo | SUCCESS | 172.22.0.3 | 0 | unlocked |

- Bloqueos activados: **1**; finalizados: **1**

## 2. Registros de acceso de los servidores web (observado)

### apache

| Código HTTP | POST /login |
|---|---|
| 302 | 2 |
| 401 | 3 |
| 429 | 2 |

- IP de origen vistas por el servidor: ['172.22.0.3']

## 3. Solicitudes capturadas por OWASP ZAP (observado)

| Código HTTP | POST /login |
|---|---|
| 302 | 2 |
| 401 | 3 |
| 429 | 2 |

## 4. Correlación de conteos

| Fuente | Intentos de login contados |
|---|---|
| Auditoría de la app | 7 |
| access.log apache | 7 |
| OWASP ZAP | 7 |

Si los números difieren, revise: pruebas previas en el mismo log, la precondición del script (1 login correcto previo), filtros de `--run-id` y que ZAP solo ve el tráfico que pasa por su proxy.

## 5. Observado vs. interpretado

- **Observado:** conteos, códigos HTTP, horas, IP y estado de bloqueo que aparecen en los archivos.
- **Interpretación (debe justificarse):** una IP por sí sola no demuestra que el intento venga de un atacante, ni si el origen es interno o externo. Cuando el tráfico pasa por ZAP, el servidor ve la IP de ZAP, no la del cliente.
- Las diferencias entre ZAP y los servidores se explican por el punto de captura (proxy vs. servidor vs. aplicación), no necesariamente por errores.
