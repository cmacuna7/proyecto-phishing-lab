# Análisis de registros

## 2. Registros de acceso de los servidores web (observado)

### apache

| Código HTTP | POST /login |
|---|---|
| 302 | 3 |
| 401 | 4 |

- IP de origen vistas por el servidor: ['172.25.0.3']

## 3. Solicitudes capturadas por OWASP ZAP (observado)

| Código HTTP | POST /login |
|---|---|
| 302 | 3 |
| 401 | 4 |

## 4. Correlación de conteos

| Fuente | Intentos de login contados |
|---|---|
| access.log apache | 7 |
| OWASP ZAP | 7 |

Si los números difieren, revise: pruebas previas en el mismo log, la precondición del script (1 login correcto previo), filtros de `--run-id` y que ZAP solo ve el tráfico que pasa por su proxy.

## 5. Observado vs. interpretado

- **Observado:** conteos, códigos HTTP, horas, IP y estado de bloqueo que aparecen en los archivos.
- **Interpretación (debe justificarse):** una IP por sí sola no demuestra que el intento venga de un atacante, ni si el origen es interno o externo. Cuando el tráfico pasa por ZAP, el servidor ve la IP de ZAP, no la del cliente.
- Las diferencias entre ZAP y los servidores se explican por el punto de captura (proxy vs. servidor vs. aplicación), no necesariamente por errores.
