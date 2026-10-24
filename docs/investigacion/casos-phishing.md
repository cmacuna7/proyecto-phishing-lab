# Casos reales de phishing con QR o enlace corto

> Fuentes revisadas el 24/10/2026. Son los dos casos que usa el informe (sección 2.4).

## Caso 1 — Estafa con códigos QR por WhatsApp en Ecuador (noviembre de 2024)
- **Fuente:** Peñafiel Robalino, M. T. (2024, 22 de noviembre). *Alerta por estafa a través de WhatsApp y códigos QR en Ecuador*. La Prensa. https://laprensa.com.ec/alerta-por-estafa-a-traves-de-whatsapp-y-codigos-qr-en-ecuador/
- **Qué pasó:** usuarios de varias provincias recibieron por WhatsApp notificaciones falsas de infracciones de tránsito, con colores y formato que imitaban avisos oficiales y un código QR que supuestamente daba información de la multa. Alertaron la Empresa de Movilidad de Cuenca y el Consejo de Seguridad Ciudadana.
- **Mecanismo:** mensaje con apariencia oficial + urgencia (multa) + QR cuyo destino no se ve antes de abrirlo.
- **Vector:** código QR en un mensaje de WhatsApp.

| Campo | Contenido |
|---|---|
| Activo afectado | Datos personales y credenciales bancarias del ciudadano; el teléfono desde el que se escanea el QR. |
| Amenaza | Delincuentes que suplantan a una entidad de tránsito. |
| Vulnerabilidad | El usuario no puede ver el destino del QR antes de abrirlo; confianza en el formato oficial; urgencia de la multa. |
| Impacto | Robo de datos personales o bancarios, fraude financiero y suplantación de identidad (según la fuente). |
| Control que habría ayudado | Concienciación (no escanear QR de canales no oficiales), canal oficial para consultar multas, vista previa del destino del QR, MFA en la banca. |
| Relación con el laboratorio | Es el escenario del afiche con QR (`/r/qr1`) y del riesgo R-02. |

## Caso 2 — Phishing a clientes de Banco Bradesco con URL acortadas de bit.ly (30 de marzo de 2011)
- **Fuente:** Segu-Info. (2011, 30 de marzo). *Phishing to Banco Bradesco abuses short URLs of bit.ly: More than 5% fall deceived*. Ventas de Seguridad. https://www.ventasdeseguridad.com/en/news/latest-news/434-computer-security/14634-phishing-to-banco-bradesco-abuses-short-urls-of-bit-ly-more-than-5-fall-deceived.html
- **Qué pasó:** correos con enlaces bit.ly llevaban a un sitio falso del banco. La estadística pública del acortador mostró 1.735 clics frente a 33.139 aperturas de la imagen del correo: una tasa de engaño de 5,24 %. El enlace se reportó hacia las 9:50 y se desactivó a las 11:46, unas dos horas después.
- **Mecanismo:** el acortador oculta el dominio real del sitio falso.
- **Vector:** enlace acortado en un correo.

| Campo | Contenido |
|---|---|
| Activo afectado | Credenciales de banca en línea de los clientes. |
| Amenaza | Phishing por correo masivo. |
| Vulnerabilidad | El enlace corto impide ver el destino; demora del proveedor en desactivar el enlace. |
| Impacto | 1.735 clics (posibles víctimas) en unas dos horas; robo de credenciales y fraude. |
| Control que habría ayudado | Expansión o vista previa de enlaces cortos en el filtro de correo, reacción rápida del proveedor del acortador, concienciación, MFA. |
| Relación con el laboratorio | Es el escenario del correo simulado (`/r/mail1`) y del riesgo R-02. |

## Caso complementario (no es de QR ni de enlace corto)
EcuCERT. (2022, 25 de febrero). *Aviso de seguridad EC-2022-41: EcuCERT advierte nueva campaña de suplantación de identidad "Banco del Pichincha"*. Correo con enlaces a un sitio que suplanta al banco para captar credenciales; riesgo alto; indicador de compromiso: un dominio ajeno al banco. Sirve como contexto ecuatoriano, pero no cumple el criterio del PDF (QR o enlace acortado).
