# Informe técnico — Simulación de phishing, monitoreo y reducción de riesgo

> ESQUELETO. Los textos marcados «BORRADOR» deben verificarse con las fuentes antes de entregar.

## Portada
- Universidad: Universidad de las Fuerzas Armadas ESPE
- Asignatura: Ingeniería de Seguridad del Software
- Título del proyecto:
- Integrantes: Marcelo Acuña, (completar)
- Docente / Fecha:

## 1. Objetivo
General y específicos (completar).

## 2. Antecedentes
### 2.1 ISO/IEC 27001 e ISO/IEC 27005 (BORRADOR)
27001: requisitos de un sistema de gestión de seguridad de la información. 27005: gestión de riesgos (establecer contexto, identificar, analizar, evaluar, tratar, aceptar, comunicar, monitorear). Relacionar cada etapa con las matrices.

### 2.2 NIST CSF 2.0 (BORRADOR)
Seis funciones: Gobernar (GV), Identificar (ID), Proteger (PR), Detectar (DE), Responder (RS), Recuperar (RC). Indicar cuáles aplica el proyecto (PR.AA, PR.AT, PR.PS, PR.DS, DE.CM, DE.AE).

### 2.3 OWASP ZAP (BORRADOR)
Proxy de interceptación; se usa para observar el tráfico HTTP del laboratorio.

### 2.4 Casos reales
Ver `docs/investigacion/casos-phishing.md`.

### 2.5 Apache vs NGINX (VERIFICAR cada fila con documentación oficial)
| Aspecto | Apache | NGINX |
|---|---|---|
| Modelo de procesamiento | | |
| Configuración | | |
| Rol en el laboratorio | Proxy inverso | Proxy inverso |
| Formato de log | combined | combined |

## 3. Diseño
- Diagrama UML: `docs/diseno-app.md`
- Diagrama de red: `docs/laboratorio.md`

## 4. Configuración e implementación
Apache, NGINX, app y ZAP, con capturas (`evidence/capturas/`).

## 5. Resultados y análisis de logs
Separar **Observado** (hechos del log) de **Interpretado** (conclusiones). Usar `evidence/analisis/*.md` y `compare_results.py`.

## 6. Matrices de riesgo
Inicial y residual (misma escala). Incluir riesgos introducidos por el control (p. ej. bloqueo usado para negar servicio a la cuenta legítima).

## 7. Conclusiones
## 8. Recomendaciones
TLS, MFA, límites por IP, centralización de logs, capacitación.

## 9. Limitaciones
HTTP sin TLS; entorno de laboratorio; una sola cuenta ficticia.

## 10. Bibliografía (APA 7)
- Route Fifty. (2022). *Cities in Texas hit by QR code phishing scam*. https://route-fifty.com/cybersecurity/2022/01/cities-texas-hit-qr-code-phishing-scam/360554
- National Institute of Standards and Technology. (2024). *The NIST Cybersecurity Framework (CSF) 2.0* (NIST CSWP 29). (completar URL/DOI)
- International Organization for Standardization. (2022). *ISO/IEC 27005:2022*. (completar)
- (completar)
