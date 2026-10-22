# Guía para explicar el proyecto (paso a paso)

## 1. En una frase
Construimos un laboratorio aislado donde simulamos un ataque de phishing (mensaje con enlace/QR hacia una app de prueba), observamos qué pasa con el tráfico y los registros, aplicamos controles (bloqueo temporal y auditoría) y medimos cómo baja el riesgo, comparando Apache y NGINX.

## 2. Qué hay en el laboratorio
| Pieza | Para qué sirve |
|---|---|
| App Flask (login con cuenta ficticia) | Es lo que "ataca" el phishing; tiene dos modos: sin controles (`baseline`) y con controles (`hardened`) |
| Apache y NGINX | Reciben las peticiones y las pasan a la misma app (proxy inverso), para compararlos |
| OWASP ZAP | Proxy que captura el tráfico HTTP (monitoreo) |
| client1 / client2 | Dos usuarios: client1 pasa por ZAP, client2 va directo |
| Docker Compose | Levanta todo en una red aislada |

## 3. Flujo del ataque simulado
1. Llega un mensaje falso (`phishing/mensaje_simulado.md`) con un enlace corto `/r/mail1` o un QR `/r/qr1`.
2. El enlace registra la visita y lleva al login del laboratorio.
3. El "atacante" prueba contraseñas (escenario S1).
4. Sin controles: puede intentar sin límite. Con controles: al 3.er fallo seguido la cuenta se bloquea 120 s, incluso la contraseña correcta se rechaza (S2), y luego vuelve a funcionar (S3).
5. Todo queda en el registro de auditoría (fecha, usuario ficticio, resultado, IP, estado de bloqueo; sin contraseñas).

## 4. Cómo se ejecuta (comandos, en PowerShell, dentro de la carpeta del proyecto)
1. Levantar: `docker compose up -d --build`
2. Comprobar: `docker compose ps` y `curl.exe -I http://127.0.0.1:8081/healthz` (Apache) / `:8082` (NGINX)
3. Estado "antes": reiniciar con `$env:CONTROLS_MODE="baseline"`, y correr `docker compose exec client1 python scripts/run_scenario.py --target apache --mode baseline` (y `nginx`)
4. Estado "después": reiniciar con `hardened` y repetir el escenario en ambos servidores
5. Exportar lo capturado por ZAP: `scripts/zap_export.py`
6. Analizar registros: `scripts/analyze_logs.py`; comparar: `scripts/compare_results.py`
7. Guardar capturas y resultados en `evidence/`

## 5. Qué respondió la prueba (observado)
Apache con controles: 3 fallos → 401 (el 3.º avisa del bloqueo); 4.º intento → 429; contraseña correcta durante el bloqueo → 429; correcta tras el bloqueo → 302. Los 6 pasos coincidieron con lo esperado.

## 6. Riesgo (matrices)
Se usa la misma escala en la matriz inicial y la residual: Riesgo = Probabilidad × Impacto (1–5): 1–4 bajo, 5–9 moderado, 10–16 alto, 17–25 crítico. El control baja la probabilidad (p. ej. fuerza bruta de 12 a 6), pero el riesgo no desaparece: queda un residual y el propio bloqueo puede usarse para negar el servicio a la cuenta legítima. Mapeo: NIST CSF 2.0 (PR.AA, PR.AT, PR.DS, DE.CM) e ISO/IEC 27005.

## 7. Qué decir con honestidad
- Observado = lo que muestran los logs y ZAP. Interpretado = nuestra conclusión sobre eso.
- Limitaciones: HTTP sin TLS, cuenta única ficticia, valores de la matriz son estimaciones justificadas con la evidencia.
- Todo es académico: sin cuentas ni sitios reales; el QR solo apunta al laboratorio.

## 8. Posibles preguntas del ingeniero
- ¿Por qué el 429 y no 401 al bloquear? Distingue "credencial inválida" de "cuenta bloqueada" y deja `Retry-After`.
- ¿Por qué no se guardan contraseñas en el log? Evita convertir el log en una fuente de credenciales; el registro tiene una lista cerrada de campos.
- ¿Qué hace distinto a Apache y NGINX aquí? Ambos actúan como proxy con el mismo log; se compara configuración, encabezados y comportamiento observado, no se asume rendimiento sin medirlo.
- ¿Qué falta? TLS, MFA, límite por IP y centralizar logs (recomendaciones).
