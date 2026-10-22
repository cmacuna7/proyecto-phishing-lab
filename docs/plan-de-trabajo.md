# Plan de trabajo

Estado: ☐ pendiente · ☑ listo en el repositorio (falta verificar en Docker/ZAP donde se indica).

## 2. Laboratorio y ejecución
- ☑ 2.1 Topología y servicios (`docker-compose.yml`) — ☐ probar `make up` en un equipo con Docker
- ☑ App de prueba con login y cuenta ficticia en ambos servidores
- ☑ Mensaje simulado y QR (`phishing/`)
- ☐ Capturar tráfico con ZAP y exportar (`make zap-export`) — probar el script
- ☑ 2.2 Registro de autenticación sin secretos
- ☑ 2.3 Bloqueo tras 3 fallos consecutivos con inicio/fin registrados
- ☐ 2.4 Ejecutar escenarios en modo `baseline` y `hardened`, en Apache y NGINX
- ☐ Generar `make analyze` y `make compare`

## 3. Documentación
- ☐ Matrices: justificar P e I con evidencia; completar columna «Evidencia»
- ☐ Informe: portada, objetivo, antecedentes (ISO 27001/27005, NIST CSF 2.0, ZAP)
- ☐ Dos casos reales de phishing con QR/enlace corto (`docs/investigacion/`)
- ☐ Tabla Apache vs NGINX (verificar cada dato con fuente oficial)
- ☐ Diagramas: UML (`docs/diseno-app.md`) y de red (`docs/laboratorio.md`)
- ☐ Capturas de configuración
- ☐ Análisis de logs (observado vs interpretado)
- ☐ Conclusiones, recomendaciones, bibliografía APA 7
- ☐ Demo corta (guion en `docs/laboratorio.md`)

## Reparto sugerido (ajustar al grupo)
| Rol | Responsabilidad |
|---|---|
| A | Laboratorio y Docker (Apache/NGINX/ZAP) |
| B | App, bloqueo y auditoría; pruebas |
| C | Matrices de riesgo y mapeo NIST/ISO |
| D | Informe, casos reales y bibliografía |
