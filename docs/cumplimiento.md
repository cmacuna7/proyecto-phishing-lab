# Cumplimiento de la actividad

Revisión del 24/10/2026 del repositorio y de [`informe/informe-tecnico.pdf`](informe/informe-tecnico.pdf) contra el enunciado [`enunciado-proyecto.pdf`](enunciado-proyecto.pdf).

✅ cumple · ⚠️ cumple parcialmente o falta aplicar en el informe · ❌ no cumple

## Resumen

El **laboratorio y el código cumplen todo** lo que pide el enunciado (secciones 2.1–2.4) y está verificado con evidencia.
Los pendientes están en el **informe PDF**: es una versión anterior a [`informe/correcciones-informe.md`](informe/correcciones-informe.md) y a la matriz actual. Hay que aplicar esas correcciones en el Word y volver a exportar.

## 2. Actividades

| # | Requisito | Estado | Dónde |
|---|---|---|---|
| 2.1.1 | Dos casos reales de phishing con QR o enlace corto | ✅ | `docs/investigacion/casos-phishing.md` |
| 2.1.2 | Activos, amenazas, vulnerabilidades e impactos de los casos | ✅ | mismo archivo + `matrices/` |
| 2.1.3 | Laboratorio aislado: 2 usuarios, Apache, NGINX, monitoreo con ZAP | ✅ | `docker-compose.yml` (contenedores, no VM; confirmar con el docente) |
| 2.1.4 | Misma app con login y cuenta ficticia en ambos servidores | ✅ | `app/`, `servers/` |
| 2.1.5 | Mensaje simulado con enlace/QR solo al laboratorio | ✅ | `phishing/` |
| 2.2.1 | Instalar y configurar ZAP | ✅ | servicio `zap` en `docker-compose.yml` |
| 2.2.2 | Capturar con ZAP solicitudes **y respuestas** | ⚠️ | `evidence/zap/*.csv` tiene método, URL y código, pero no hay captura de pantalla de ZAP con una solicitud/respuesta completa |
| 2.2.3 | Intentos fallidos y exitosos con datos ficticios | ✅ | `evidence/resultados/` |
| 2.2.4 | Registros de Apache, NGINX y la app | ✅ | `evidence/logs/` |
| 2.2.5 | Capturas de configuración, solicitudes HTTP y registros | ⚠️ | `evidence/capturas/` (11 figuras + 2 diagramas); falta la de ZAP (ver 2.2.2) |
| 2.3.1 | Registro con fecha, usuario, resultado, IP y estado de bloqueo | ✅ | `app/labapp/audit.py` |
| 2.3.2 | Bloqueo tras 3 fallos consecutivos | ✅ | `app/labapp/auth.py`, `app/tests/` |
| 2.3.3 | Contraseña correcta rechazada durante el bloqueo | ✅ | paso S2 → 429 en ambos servidores. Desde el navegador no se probó (ver Fig. 8) |
| 2.3.4–6 | Matriz inicial, controles ISO 27005 / NIST CSF 2.0, matriz residual | ✅ | `matrices/matriz_riesgos.xlsx` (R-01 a R-07) |
| 2.4.1 | Pruebas antes y después de los controles | ✅ | `evidence/resultados/` (baseline y hardened) |
| 2.4.2 | Comparar Apache y NGINX en las mismas condiciones | ✅ | `evidence/analisis/comparacion.md` |
| 2.4.3 | Reconstruir la secuencia de intentos y el bloqueo con los registros | ✅ | `evidence/analisis/*_hardened.md` |
| 2.4.4 | Presentar resultados, limitaciones y recomendaciones | ✅ | informe, secciones 7–9 |

## 3. Estructura del informe técnico (PDF)

| # | Requisito | Estado | Qué falta |
|---|---|---|---|
| 3.1 | Portada con el título exigido | ❌ | El título debe ser literal: *Monitoreo de seguridad: simulación de phishing, análisis de eventos y reducción de riesgos* (correcciones, punto 0) |
| 3.2 | Objetivo | ✅ | |
| 3.3.1 | ISO/IEC 27001 y 27005 | ⚠️ | Quitar la nota interna "verifíquela…" (punto 1) |
| 3.3.2 | NIST CSF 2.0, seis funciones | ✅ | |
| 3.3.3 | ZAP: qué es, características y **requisitos** | ⚠️ | Faltan los requisitos de funcionamiento (Java 17 / Docker) (punto 2) |
| 3.3.4 | Casos reales | ⚠️ | Corregir dos datos del caso Bradesco (punto 3) |
| 3.3.5 | Cuadro Apache vs NGINX | ⚠️ | Faltan "registros" y "requisitos de funcionamiento" (punto 4) |
| 3.4.1 | Diagrama UML y diagrama de red | ✅ | |
| 3.4.2–3 | Configuración de Apache/NGINX y **ubicación de los registros** | ⚠️ | Agregar la tabla de ubicación de logs (punto 7) |
| 3.4.4 | Funcionalidades de la app | ✅ | |
| 3.4.5 | ZAP: mostrar solicitudes y respuestas con capturas | ⚠️ | Figura 9 es el CSV en GitHub, no ZAP. Agregar captura de la respuesta 429 (punto 7, "Recomendado") |
| 3.5.1 | Análisis de registros, observado vs interpretado | ✅ | |
| 3.5.2 | Matriz inicial con todas las columnas | ⚠️ | La tabla del PDF no muestra vulnerabilidad, escenario ni controles existentes (sí están en el Excel). Falta R-07 (punto 13) |
| 3.5.3 | Matriz residual con todas las columnas | ⚠️ | Faltan ISO 27005, evidencia y riesgo que permanece (están en el Excel). Valores de R-02 desactualizados (el PDF dice 12, el Excel 16) |
| 3.5.4 | Tabla antes/después | ✅ | Ajustar según el punto 9 |
| 3.6 | Conclusiones | ⚠️ | La conclusión 3 dice "el bloqueo duró exactamente 120 s"; corregir (puntos 10 y 14) |
| 3.7 | Recomendaciones | ✅ | |
| 3.8 | Bibliografía APA 7 con documentación **oficial** de Apache, NGINX y ZAP | ⚠️ | Falta documentación oficial de NGINX (solo hay un blog) y de los logs de Apache; uniformar citas ISO (punto 17) |

## 4. Entregables

| Entregable | Estado |
|---|---|
| Informe técnico | ⚠️ aplicar `informe/correcciones-informe.md` y reexportar el PDF |
| Evidencias (diagramas, capturas, logs, resultados) | ✅ `evidence/` (falta la captura de ZAP) |
| Matrices inicial y residual | ✅ `matrices/matriz_riesgos.xlsx` |
| Demostración | ✅ guion en `docs/laboratorio.md`; ensayar la contraseña correcta durante el bloqueo desde el navegador |

## Para cerrar los pendientes

1. Aplicar los puntos 0–17 de [`informe/correcciones-informe.md`](informe/correcciones-informe.md) en el Word y revisar la lista del punto 18.
2. Sacar la captura de ZAP: levantar con la interfaz gráfica (ver README) o abrir `http://127.0.0.1:8090/JSON/core/view/message/?id=<id>` de una respuesta 429, **tapando la contraseña**. Guardarla en `evidence/capturas/` y agregarla al informe.
3. Reemplazar `informe/informe-tecnico.pdf` con el PDF corregido.
