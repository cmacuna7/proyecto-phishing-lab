# Comparación antes y después / Apache vs NGINX

| Criterio | apache · baseline | nginx · baseline | apache · hardened | apache · hardened | nginx · hardened |
|---|---|---|---|---|---|
| Intentos fallidos ejecutados | 4 | 4 | 4 | 4 | 4 |
| Intentos registrados por la app (auditoría) | 0 (sin auditoría) | 0 (sin auditoría) | 6 | 6 | 6 |
| Bloqueo activado al 3.er fallo consecutivo | No | No | Sí | Sí | Sí |
| 4.º intento fallido (HTTP) | 401 | 401 | 429 | 429 | 429 |
| Credenciales correctas durante el bloqueo (HTTP) | 302 | 302 | 429 | 429 | 429 |
| Credenciales correctas tras finalizar el bloqueo (HTTP) | 302 | 302 | 302 | 302 | 302 |
| Todos los pasos coinciden con lo esperado | Sí | Sí | Sí | Sí | Sí |
| Nivel de riesgo estimado de fuerza bruta (R-01) | 12 (Alto) | 12 (Alto) | 9 (Moderado) | 9 (Moderado) | 9 (Moderado) |

Notas: 'baseline' = sin controles; 'hardened' = con bloqueo y registro de auditoría. Las diferencias entre Apache y NGINX deben explicarse en el informe a partir de los registros.
