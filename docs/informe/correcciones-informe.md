# Correcciones del informe técnico (para pegar en el Word)

Revisión del 24/10/2026 contra el PDF del proyecto (`docs/enunciado-proyecto.pdf`) y la evidencia del repositorio.
Cada punto indica **dónde** va, **qué hacer** y el **texto nuevo**. Los números de sección son los del informe actual.

> Para pegar tablas: abra este archivo en VS Code, abra la vista previa (`Ctrl+Shift+V`) y copie desde ahí;
> Word las pega como tablas.

---

## 0. Portada (requisito 3.1)

**Acción:** cambiar el título. El PDF exige este título literal.

> **Monitoreo de seguridad: simulación de phishing, análisis de eventos y reducción de riesgos**

Cambiar también el encabezado de la primera página ("Informe técnico — Simulación de phishing, monitoreo y reducción de riesgo").

---

## 1. Sección 2.1 — quitar la nota interna

**Acción:** reemplazar el párrafo que empieza "El proyecto sigue el proceso general…" (incluye la nota "verifíquela con la copia de la universidad antes de entregar").

> El proyecto sigue el proceso de gestión de riesgos que describe la norma, alineado con ISO 31000: establecer el contexto; evaluar el riesgo (identificarlo, analizarlo y valorarlo); tratarlo; aceptar el riesgo residual; y, de forma transversal, comunicar y consultar, y hacer seguimiento y revisión. La tabla siguiente muestra dónde aparece cada etapa en el proyecto.

(La limitación de no haber consultado el texto completo ya está en la sección 9; no hace falta repetirla aquí.)

---

## 2. Sección 2.3 — ZAP (requisito 3.3.3: qué es, para qué sirve, características y requisitos)

**Acción:** reemplazar la sección completa.

> **2.3 ZAP (Zed Attack Proxy)**
>
> **Qué es.** ZAP es una herramienta libre y de código abierto para pruebas de seguridad de aplicaciones web. Su núcleo es un proxy intermediario: se sitúa entre el navegador y la aplicación y permite ver "all of the requests you make to a web app and all of the responses you receive from it", además de modificarlas al vuelo con puntos de interrupción (ZAP, s. f.-a).
>
> **Para qué sirve.** Para observar y registrar el tráfico HTTP de una aplicación, analizarlo en busca de problemas de seguridad y, cuando está autorizado, probar ataques contra ella.
>
> **Características técnicas principales.**
> - Proxy de interceptación con historial de todas las solicitudes y respuestas, y puntos de interrupción.
> - Árbol de sitios con los recursos descubiertos.
> - Escáner pasivo, que analiza el tráfico sin enviar peticiones nuevas, y escáner activo, que envía ataques.
> - Arañas (spider tradicional y AJAX) para descubrir contenido.
> - Fuzzer y editor de solicitudes.
> - API REST para controlarlo desde scripts, y modo *daemon* sin interfaz gráfica.
> - Ampliable con complementos (*add-ons*) y con un marco de automatización.
>
> **Requisitos de funcionamiento.** Las versiones para Windows y Linux requieren Java 17 o superior; la de macOS incluye Java. También se distribuye como imagen de Docker (stable, bare, weekly y nightly), que ya trae todo lo necesario (ZAP, s. f.-b).
>
> **Uso en el laboratorio.** Se usó la imagen `ghcr.io/zaproxy/zaproxy:stable` en modo daemon, como proxy en el puerto 8090, solo para observar: el usuario 1 navega a través de ZAP y el usuario 2 va directo, para comparar lo que ve cada punto de captura. No se usó el escáner activo ni la interfaz gráfica.

---

## 3. Sección 2.4 — casos reales (requisito 3.3.4: fuente, mecanismo, activos, consecuencias y controles)

**Acción:** reemplazar la tabla y el párrafo siguiente. Hay dos datos que corregir en el caso Bradesco:
- El 5,24 % son personas **engañadas** (1.735 clics frente a 33.139 aperturas del correo), no personas que lo reportaron.
- El enlace estuvo activo unas **dos horas** después del reporte (reportado a las 9:50, desactivado a las 11:46).

| | Caso 1: QR por WhatsApp (Ecuador, 2024) | Caso 2: enlaces bit.ly contra Bradesco (2011) |
|---|---|---|
| Fuente | Peñafiel Robalino (2024), La Prensa | Segu-Info (2011), Ventas de Seguridad |
| Qué pasó | Usuarios de varias provincias recibieron por WhatsApp notificaciones falsas de infracciones de tránsito, con formato y colores oficiales y un código QR "con información de la multa". Alertaron la Empresa de Movilidad de Cuenca y el Consejo de Seguridad Ciudadana. | Correos con enlaces bit.ly llevaban a un sitio falso del banco. La estadística del acortador mostró 1.735 clics frente a 33.139 aperturas del correo: 5,24 % de engaño. El enlace se desactivó unas dos horas después del reporte. |
| Mecanismo | Mensaje con apariencia oficial y urgencia (multa) + QR cuyo destino no se ve antes de abrirlo | Enlace acortado que oculta el dominio real del sitio falso |
| Activos afectados | Datos personales y credenciales bancarias del ciudadano; su teléfono | Credenciales de banca en línea de los clientes |
| Amenaza y vulnerabilidad | Suplantación de una entidad de tránsito; el usuario no ve el destino del QR y confía en el formato oficial | Phishing masivo por correo; el enlace corto oculta el destino y el proveedor tardó en desactivarlo |
| Consecuencias | Robo de datos personales o bancarios, fraude financiero y suplantación de identidad | 1.735 posibles víctimas en unas dos horas; robo de credenciales y fraude |
| Controles que reducirían el riesgo | Concienciación (no escanear QR de canales no oficiales), canal oficial para consultar multas, vista previa del destino del QR, MFA en la banca | Expansión o vista previa de enlaces cortos en el filtro de correo, reacción rápida del acortador, concienciación, MFA |
| Relación con el laboratorio | Afiche con QR (`/r/qr1`), riesgo R-02 | Correo simulado (`/r/mail1`), riesgo R-02 |

> El caso del QR en WhatsApp es el más cercano al laboratorio: un mensaje que aparenta ser oficial y un QR cuyo destino no se ve antes de abrirlo. Como complemento ecuatoriano se revisó el aviso EC-2022-41 de EcuCERT sobre una campaña de suplantación del Banco Pichincha por correo (riesgo alto); no se incluye como caso principal porque no usa QR ni enlaces acortados.

---

## 4. Sección 2.5 — Apache frente a NGINX (requisito 3.3.5: faltan "registros" y "requisitos de funcionamiento")

**Acción:** agregar estas filas a la tabla existente.

| Aspecto | Apache HTTP Server 2.4 | NGINX | Tipo de dato |
|---|---|---|---|
| Registros: ubicación | `CustomLog "logs/access.log" combined` y `ErrorLog "logs/error.log"` (en el contenedor `/usr/local/apache2/logs/`; en el anfitrión `logs/apache/`) | `access_log /var/log/nginx/access.log` y `error_log /var/log/nginx/error.log` (en el anfitrión `logs/nginx/`) | Observado (configuración) |
| Registros: hora anotada | `%t`: hora en que se **recibió** la solicitud (Apache Software Foundation, s. f.-c) | `$time_local`: hora local en formato Common Log; la línea se escribe al terminar la respuesta (NGINX, s. f.-b) | Documentación |
| Registros: diferencia observada | El 3.er fallo del escenario quedó a las 18:05:26, igual que en la aplicación | El 3.er fallo quedó a las 18:07:48, aunque la aplicación lo registró a las 18:07:47.967: NGINX anota la hora al terminar la respuesta | Observado |
| Tamaño de las respuestas | 401 = 2532 bytes; 429 = 2564 | 401 = 2531 bytes; 429 = 2563 | Observado; la diferencia de 1 byte es la etiqueta "apache"/"nginx" del pie de página |
| Requisitos de funcionamiento | Módulos cargados explícitamente: `mod_proxy`, `mod_proxy_http`, `mod_headers`, `mod_log_config`, MPM `event`. Imagen oficial `httpd:2.4` | Proxy y registros incluidos en el núcleo (`ngx_http_proxy_module`, `ngx_http_log_module`). En Docker necesita `resolver` para resolver nombres de servicios en tiempo de ejecución. Imagen oficial `nginx:1.27-alpine` | Observado + documentación |

---

## 5. Sección 3.2 — diagrama UML de secuencia (requisito 3.4.1)

**Acción:** rehacer la figura. El diagrama actual tiene cuatro problemas:
1. El fragmento combinado se llama `alt` en UML, no "según".
2. Muestra `LOCKOUT_START` en cada fallo, pero solo ocurre en el 3.º: debe ir dentro de un `opt [fallos = 3]`.
3. No muestra la validación de credenciales (el PDF la pide).
4. No muestra quién escribe `LOCKOUT_END`.

El diagrama corregido está en [`docs/diseno-app.md`](../diseno-app.md), en formato Mermaid. Péguelo en https://mermaid.live, exporte en PNG y reemplace la figura.

**Pie de figura nuevo:**

> Diagrama de secuencia UML (modo con controles). La aplicación lee el estado de la cuenta en una transacción; si está bloqueada responde 429 sin evaluar la contraseña; si no, valida el hash PBKDF2. Al 3.er fallo consecutivo registra LOCKOUT_START, y un hilo de barrido registra LOCKOUT_END cuando vence el bloqueo.

---

## 6. Sección 4.2 — bloqueo temporal: corregir el último punto

**Acción:** reemplazar "Los usuarios inexistentes no generan bloqueo, para no revelar qué cuentas existen."

> · Los usuarios inexistentes no generan bloqueo (no se guarda estado de nombres que no existen). Esto tiene un costo: como solo una cuenta real puede llegar a responder 429, tres fallos bastan para saber si una cuenta existe. El hash de relleno solo evita que el tiempo de la respuesta 401 delate al usuario.

---

## 7. Secciones 4.4 y 4.5 — ubicación de los registros y configuración de ZAP (requisitos 3.4.2, 3.4.3 y 3.4.5)

**Acción:** agregar al final de 4.4:

> **Ubicación de los registros.** Cada contenedor escribe en un volumen montado en la carpeta del proyecto, para poder copiarlos a la evidencia:
>
> | Registro | Dentro del contenedor | En el anfitrión |
> |---|---|---|
> | Apache, acceso y errores | `/usr/local/apache2/logs/access.log`, `error.log` | `logs/apache/` |
> | NGINX, acceso y errores | `/var/log/nginx/access.log`, `error.log` | `logs/nginx/` |
> | Aplicación detrás de Apache | `/var/log/lab-app/auth.log` | `logs/app-apache/auth.log` |
> | Aplicación detrás de NGINX | `/var/log/lab-app/auth.log` | `logs/app-nginx/auth.log` |
>
> Los registros de cada corrida se copiaron a `evidence/logs/baseline/` y `evidence/logs/hardened/` antes de reiniciar el laboratorio.

**Acción:** agregar al final de 4.5:

> **Campos analizados.** De cada mensaje capturado se exportan: identificador, hora, método, URL, código de respuesta, tiempo de ida y vuelta (`rtt_ms`) y el encabezado `X-Lab-Run`, que identifica la corrida del escenario y permite correlacionar ZAP con `auth.log` (campo `run_id`). Los campos del formulario se exportan enmascarados (`username=***&password=***`).

**Recomendado (requisito 3.4.5, "mostrar solicitudes y respuestas"):** el CSV no muestra encabezados ni cuerpo. Si hay tiempo, conviene agregar una figura con una respuesta completa:
1. Levante el laboratorio en modo hardened y ejecute el escenario en Apache.
2. Exporte el CSV con `zap_export.py`, busque el `id` de la primera fila con 429 (en la corrida del 22/10 era el 6) y abra `http://127.0.0.1:8090/JSON/core/view/message/?id=<id>` en el navegador.
3. Capture `responseHeader`, que muestra `HTTP/1.1 429` y `Retry-After`.
4. **Tape la contraseña** del `requestBody` antes de capturar.

---

## 8. Sección 4.6 — pie de la Figura 1

**Acción:** reemplazar.

> Figura 1. Encabezados de respuesta de Apache y NGINX con curl -I: Server muestra solo "Apache" o "nginx" (sin gunicorn ni versión), y la aplicación agrega X-Content-Type-Options: nosniff y Cache-Control: no-store.

---

## 9. Sección 5.1 — tabla de resultados (requisito 3.5.4)

**Acción:** agregar estas filas a la tabla (antes de "Todos los pasos como se esperaba"). Las dos últimas son las que exige el PDF y faltan.

| Paso | Apache sin controles | NGINX sin controles | Apache con controles | NGINX con controles |
|---|---|---|---|---|
| Intentos fallidos ejecutados | 4 | 4 | 4 | 4 |
| Intentos contados en access.log / ZAP | 7 / 7 | 7 / 7 | 7 / 7 | 7 / 7 |
| Diferencias entre Apache y NGINX | Ninguna en los códigos HTTP | | Ninguna en los códigos HTTP ni en el bloqueo | |
| Nivel de riesgo de fuerza bruta (R-01) | 12 (Alto) | 12 (Alto) | 9 (Moderado) | 9 (Moderado) |

(Las únicas diferencias entre servidores son de registro: la hora que anota cada uno y 1 byte de tamaño; ver la tabla de la sección 2.5.)

---

## 10. Sección 5.2 — "el bloqueo duró exactamente 120 segundos"

**Acción:** reemplazar la frase final de 5.2.

> LOCKOUT_START (18:05:26.536) y LOCKOUT_END (18:07:26.536) están separados por 120 segundos. LOCKOUT_END se registra con la hora programada de fin; el hilo de barrido revisa los bloqueos cada segundo, así que el desbloqueo real ocurre como mucho un segundo después. Lo comprobado por el escenario es que la contraseña correcta fue rechazada durante el bloqueo (18:05:26.688) y aceptada después de que terminó (18:07:29.730). NGINX registró la misma secuencia.

---

## 11. Sección 5.3 — diferencia de tiempo entre ZAP y la aplicación

**Acción:** reemplazar la frase "ZAP marca cada petición unas decenas de milisegundos antes…".

> ZAP marca cada petición entre 2 y 23 milisegundos antes que la aplicación (2 a 3 ms en la mayoría; por ejemplo, 18:05:26.347 en ZAP y 18:05:26.349 en la aplicación). Es coherente con que ZAP está antes en el camino.

**Acción:** completar la frase sobre las 8 filas:

> El CSV de ZAP tiene 8 filas, no 7: la primera (id 2 en Apache, id 10 en NGINX) es un GET http://apache sin código de respuesta y con fecha 1970-01-01. No corresponde a una petición del escenario y no se cuenta.

---

## 12. Sección 5.5 — observado frente a interpretado

**Acción:** reemplazar estas tres filas y agregar una cuarta.

| Observado | Interpretado |
|---|---|
| La IP de origen en los registros del escenario fue 172.22.0.7 en la corrida sin controles y 172.22.0.3 en la corrida con controles; en las pruebas desde el navegador fue 172.22.0.1 | Las dos primeras corresponden al contenedor de ZAP (el laboratorio se recreó entre corridas y cambió su IP); 172.22.0.1 es la puerta de enlace de la red de Docker, por la que entra el navegador del anfitrión |
| Los usuarios desconocidos no se bloquean | Evita guardar estado de nombres inexistentes, pero deja sin límite el sondeo de nombres y permite saber qué cuentas existen (solo una cuenta real llega a dar 429) |
| La primera fila del CSV de ZAP (id 2 / id 10) no tiene código ni fecha válida | Parece un nodo del árbol de sitios de ZAP y no tráfico real; no se verificó |
| Con controles, las respuestas 429 tardaron 17–26 ms en ZAP y las 401, 69–82 ms | El bloqueo responde sin calcular el hash PBKDF2, que es lo costoso; coincide con el código |

**Sobre la verificación de la IP:** si el equipo tiene una captura de `docker network inspect seg-phishing-lab_lab-net`, agréguela como figura y escriba "verificado con docker network inspect (Figura N)". Si no la tiene, deje el texto como está arriba (sin "verificado"). Ojo: como la red se recrea en cada `docker compose down`, una inspección hecha hoy no prueba las IP del 22/10.

---

## 13. Sección 6 — matrices

### 13.1 Párrafo inicial

**Acción:** reemplazar.

> Los controles bajaron de Alto a Moderado los riesgos de fuerza bruta (R-01) y de falta de trazabilidad (R-03). R-02, R-04, R-05 y R-06 no cambiaron de nivel. El bloqueo introdujo un riesgo nuevo, R-07 (bloqueo malicioso de la cuenta), que pasó de Bajo (2) a Moderado (8). Las dos matrices usan la misma escala, y el archivo completo, con la justificación de cada valor, está en matrices/matriz_riesgos.xlsx.

### 13.2 Matriz inicial completa (requisito 3.5.2)

**Acción:** reemplazar la tabla 6.2. El PDF exige vulnerabilidad, escenario y controles existentes. Conviene poner esta sección en orientación horizontal.

| ID | Activo | Amenaza | Vulnerabilidad | Escenario de riesgo | I | P | Nivel | Controles existentes |
|---|---|---|---|---|---|---|---|---|
| R-01 | Cuenta ficticia «usuario.demo» en el formulario /login | Fuerza bruta o adivinación de contraseñas | La aplicación acepta intentos ilimitados | Un atacante automatiza intentos hasta adivinar la contraseña y entra a la cuenta | 3 | 4 | 12 Alto | Hash PBKDF2 y mensaje de error genérico; sin bloqueo ni auditoría |
| R-02 | Credenciales del funcionario expuestas a un mensaje con QR o enlace corto | Phishing | El usuario no ve el destino del QR o del enlace corto; sin MFA; poca concienciación | El usuario escanea el QR, entrega sus credenciales y el atacante las reutiliza | 4 | 4 | 16 Alto | Ninguno |
| R-03 | Registros de acceso (auth.log y access.log) | Incidente sin detección ni reconstrucción posible | La aplicación no registra eventos de autenticación; el access.log no muestra usuario ni estado de bloqueo | Hay intentos repetidos y nadie puede reconstruir la secuencia | 3 | 4 | 12 Alto | Solo el access.log del servidor |
| R-04 | Servidor web Apache | Reconocimiento y explotación de fallas conocidas | Los encabezados revelan la tecnología interna (Server: gunicorn); configuración por defecto | El atacante identifica la tecnología y prueba exploits conocidos | 3 | 3 | 9 Moderado | Ninguno |
| R-05 | Servidor web NGINX | Reconocimiento y explotación de fallas conocidas | Igual que R-04 | Igual que R-04, sobre NGINX | 3 | 3 | 9 Moderado | Ninguno |
| R-06 | Tráfico HTTP de autenticación | Interceptación en la red | HTTP sin TLS | Un equipo de la misma red captura el POST /login y obtiene usuario y contraseña | 4 | 3 | 12 Alto | Red aislada del laboratorio |
| R-07 | Cuenta ficticia «usuario.demo» (disponibilidad del acceso legítimo) | Bloqueo malicioso de la cuenta | Sin bloqueo no existe: es un riesgo que aparece con el control | Un atacante que conoce el nombre de la cuenta la bloquea con 3 fallos cada 120 s | 2 | 1 | 2 Bajo | No aplica |

### 13.3 Matriz residual completa (requisito 3.5.3)

**Acción:** reemplazar la tabla 6.3. El PDF exige la relación con ISO 27005, la evidencia y el riesgo que permanece.

| ID | Control implementado | ISO/IEC 27005 | NIST CSF 2.0 | Evidencia de funcionamiento | P | I | Nivel | Var. | Riesgo que permanece y acciones |
|---|---|---|---|---|---|---|---|---|---|
| R-01 | Bloqueo de 120 s tras 3 fallos consecutivos, mensaje informativo, registro de inicio y fin | Tratamiento: modificar | PR.AA, DE.CM | Con controles, 4.º fallo = 429 y clave correcta durante el bloqueo = 429; sin controles = 401 y 302 (Apache y NGINX) | 3 | 3 | 9 Moderado | −3 | Ataque lento (~90 intentos/hora por cuenta) o desde varias IP. Límite por IP, MFA, alertas |
| R-02 | Registro de la visita al enlace (LINK_VISIT); MFA y capacitación solo recomendados | Tratamiento: modificar (parcial); compartir con el usuario mediante concienciación | PR.AT, PR.AA, DE.AE | /r/qr1 registra LINK_VISIT (afiche-qr), Figura 8. La clave correcta entra también con controles (S3 = 302) | 4 | 4 | 16 Alto | 0 | Igual: LINK_VISIT solo detecta y el bloqueo no impide usar una clave entregada. MFA, capacitación, filtrado de QR y enlaces |
| R-03 | Registro de auditoría sin contraseñas ni tokens | Seguimiento y revisión; tratamiento: modificar | DE.CM, DE.AE | Auditoría = access.log = ZAP = 7 intentos; la secuencia se reconstruye completa | 3 | 3 | 9 Moderado | −3 | Logs en el mismo host, sin alertas ni integridad. Servidor central (SIEM), retención, control de acceso |
| R-04 | Ocultar la tecnología y la versión (ServerTokens Prod, Header Server), TraceEnable Off | Tratamiento: modificar (menos exposición) | PR.PS | curl -I: Server: Apache, sin gunicorn (Figura 1) | 3 | 3 | 9 Moderado | 0 | Menos información, pero no menos explotable. Parches, escaneo de vulnerabilidades |
| R-05 | server_tokens off, proxy_hide_header Server | Tratamiento: modificar (menos exposición) | PR.PS | curl -I: Server: nginx, sin versión ni gunicorn (Figura 1) | 3 | 3 | 9 Moderado | 0 | Igual que R-04 |
| R-06 | Ninguno; se recomienda TLS | Retener temporalmente (laboratorio aislado) | PR.DS | ZAP captura los POST http://…/login sin cifrado | 3 | 4 | 12 Alto | 0 | Igual. Habilitar HTTPS con TLS y HSTS |
| R-07 | Ninguno específico; el bloqueo dura 120 s y se libera solo, y LOCKOUT_START/LOGIN_BLOCKED permiten detectarlo | Riesgo nuevo identificado en el seguimiento; retener temporalmente | ID.RA, DE.CM, DE.AE | 3 fallos desde el navegador bloquearon la cuenta a las 18:19:34 (Figura 8); S2 = 429 con la clave correcta | 4 | 2 | 8 Moderado | +6 | Bloqueo indefinido repitiendo 3 fallos cada 120 s. Límite por IP, retardo progresivo o CAPTCHA, alerta ante bloqueos repetidos |

### 13.4 Justificaciones (reemplazar los tres ejemplos)

> · **R-01.** La probabilidad bajó de 4 a 3 porque con controles solo caben 3 intentos cada 120 segundos (unos 90 por hora por cuenta), frente a intentos ilimitados sin controles. No bajó a 2 porque un ataque lento sigue siendo posible y los usuarios desconocidos nunca se bloquean.
>
> · **R-02.** No baja. El registro LINK_VISIT permite detectar quién abrió el enlace, pero no impide que el usuario entregue su contraseña, y con la contraseña correcta el acceso entra también con controles. MFA y capacitación no se implementaron, y un control no implementado no reduce el riesgo.
>
> · **R-04 y R-05.** Ocultar la versión reduce la información visible para un atacante, pero no hay evidencia de que el servidor sea menos explotable, por lo que no se bajó el nivel.
>
> · **R-07.** Sube de 2 a 8. Sin bloqueo el escenario no puede ocurrir (P = 1); con bloqueo bastan 3 intentos fallidos desde cualquier IP y el nombre de la cuenta aparece en el propio mensaje de phishing (P = 4). El impacto es menor (I = 2): se pierde temporalmente el acceso a una cuenta, sin exponer datos.

### 13.5 Sección 6.4

**Acción:** reemplazar el párrafo (quita la nota "debe discutirse en las conclusiones").

> **6.4 Riesgo que introduce el propio control (R-07)**
>
> El bloqueo temporal puede usarse para negar el servicio: cualquiera que conozca el nombre de la cuenta puede mantenerla bloqueada repitiendo tres intentos fallidos cada 120 segundos. Este riesgo no existía antes del control, por eso se agregó a ambas matrices como R-07 (de 2, Bajo, a 8, Moderado). Que un control reduzca un riesgo e introduzca otro es parte del análisis de tratamiento: el riesgo residual total no es solo la suma de las reducciones.

### 13.6 Sección 6.5

**Acción:** agregar una fila a la tabla.

| Etapa de ISO/IEC 27005 | Función NIST CSF 2.0 | Evidencia en el proyecto |
|---|---|---|
| Seguimiento y revisión: identificación de un riesgo nuevo | Identificar (ID.RA) | R-07, bloqueo malicioso introducido por el control |

---

## 14. Sección 7 — conclusiones 2, 3 y 5

**Acción:** reemplazar.

> 2. **El riesgo bajó, pero no desapareció.** La fuerza bruta (R-01) y la falta de trazabilidad (R-03) pasaron de Alto (12) a Moderado (9). El phishing (R-02) siguió en Alto (16) y el tráfico sin cifrar (R-06) en Alto (12), porque el bloqueo no impide usar una contraseña ya entregada ni cifra el tráfico.
>
> 3. **La trazabilidad quedó verificada.** La auditoría de la aplicación, el access.log y ZAP contaron 7 intentos cada uno en ambos servidores, con los mismos códigos. La secuencia LOGIN_FAILED → LOCKOUT_START → LOGIN_BLOCKED → LOCKOUT_END → LOGIN_SUCCESS permite reconstruir el bloqueo completo, y LOCKOUT_START y LOCKOUT_END están separados por los 120 segundos configurados.
>
> 5. **El control introduce un riesgo propio.** Cualquiera que conozca un nombre de cuenta puede bloquearla repitiendo tres intentos fallidos cada 120 segundos (R-07, de 2 a 8). Además, como los usuarios inexistentes nunca se bloquean, la respuesta 429 revela qué cuentas existen.

---

## 15. Sección 8 — recomendaciones (agregar filas)

| Recomendación | Riesgo que atiende | Categoría NIST CSF 2.0 |
|---|---|---|
| Sustituir el bloqueo total por un retardo progresivo o CAPTCHA, y alertar ante bloqueos repetidos de una misma cuenta | R-07, R-01 | PR.AA, DE.AE |
| Responder igual a usuarios existentes e inexistentes (bloquear también por nombre de usuario desconocido) | R-01, R-07 | PR.AA |
| Procedimiento para que los usuarios reporten mensajes sospechosos y plan de respuesta ante credenciales comprometidas (cambio de contraseña, revisión de accesos) | R-02 | RS.MA, RS.AN |
| Revisar la matriz de riesgos periódicamente y asignar un responsable de aceptar el riesgo residual | Todos | GV.RM |

---

## 16. Sección 9 — limitaciones

**Acción:** reemplazar el punto "La IP de origen mostrada en los registros… se verificó con docker network inspect" (no es una limitación). Si no hay captura de la verificación, use:

> · La asociación de las IP 172.22.0.7 y 172.22.0.3 con ZAP, y de 172.22.0.1 con la puerta de enlace de Docker, es una interpretación: la red se recrea en cada reinicio y no se guardó una inspección de la red en el momento de las pruebas.

**Acción:** agregar:

> · Las pruebas manuales desde el navegador (enlace /r/qr1, usuario desconocido y bloqueo de las 18:19:34) solo quedaron en la captura del auth.log (Figura 8); los registros de evidence/logs/ se copiaron antes de esas pruebas.
>
> · LOCKOUT_END se registra con la hora programada de fin del bloqueo, no con la hora exacta del desbloqueo (que ocurre como mucho un segundo después).
>
> · ZAP solo capturó el tráfico del usuario 1; no se usaron su interfaz gráfica ni su escáner activo.

---

## 17. Sección 10 — bibliografía (requisito 3.8: documentación oficial de Apache, NGINX y ZAP)

**Acción:** corregir el autor de las normas ISO (no es "IEC Webstore") y el título del aviso de EcuCERT. Agregar la documentación oficial de NGINX (el blog de Garrett no lo es), la de Apache sobre proxy y registros, y la de ZAP sobre requisitos. Lista completa en orden alfabético:

Apache Software Foundation. (s. f.-a). *Apache MPM event*. Apache HTTP Server Version 2.4 Documentation. https://httpd.apache.org/docs/2.4/mod/event.html

Apache Software Foundation. (s. f.-b). *Apache module mod_proxy*. Apache HTTP Server Version 2.4 Documentation. https://httpd.apache.org/docs/2.4/mod/mod_proxy.html

Apache Software Foundation. (s. f.-c). *Apache module mod_log_config*. Apache HTTP Server Version 2.4 Documentation. https://httpd.apache.org/docs/2.4/mod/mod_log_config.html

EcuCERT. (2022, 25 de febrero). *Aviso de seguridad EC-2022-41: EcuCERT advierte nueva campaña de suplantación de identidad "Banco del Pichincha"*. Centro de Respuesta a Incidentes Informáticos del Ecuador. https://www.ecucert.gob.ec/wp-content/uploads/2022/04/EC-2022-41-Aviso-de-seguridad-Campana-de-phishing-Banco-Pichincha-1.pdf

Garrett, O. (2015, 10 de junio). *Inside NGINX: How we designed for performance & scale*. NGINX Community Blog. https://blog.nginx.org/blog/inside-nginx-how-we-designed-for-performance-scale

International Organization for Standardization & International Electrotechnical Commission. (2022a). *ISO/IEC 27001:2022. Information security, cybersecurity and privacy protection — Information security management systems — Requirements* (3.ª ed.). https://webstore.iec.ch/publication/79694

International Organization for Standardization & International Electrotechnical Commission. (2022b). *ISO/IEC 27005:2022. Information security, cybersecurity and privacy protection — Guidance on managing information security risks* (4.ª ed.). https://webstore.iec.ch/publication/79713

National Institute of Standards and Technology. (2024). *The NIST Cybersecurity Framework (CSF) 2.0* (NIST CSWP 29). https://doi.org/10.6028/NIST.CSWP.29

NGINX. (s. f.-a). *Module ngx_http_proxy_module*. nginx documentation. https://nginx.org/en/docs/http/ngx_http_proxy_module.html

NGINX. (s. f.-b). *Module ngx_http_log_module*. nginx documentation. https://nginx.org/en/docs/http/ngx_http_log_module.html

Peñafiel Robalino, M. T. (2024, 22 de noviembre). *Alerta por estafa a través de WhatsApp y códigos QR en Ecuador*. La Prensa. https://laprensa.com.ec/alerta-por-estafa-a-traves-de-whatsapp-y-codigos-qr-en-ecuador/

Segu-Info. (2011, 30 de marzo). *Phishing to Banco Bradesco abuses short URLs of bit.ly: More than 5% fall deceived*. Ventas de Seguridad. https://www.ventasdeseguridad.com/en/news/latest-news/434-computer-security/14634-phishing-to-banco-bradesco-abuses-short-urls-of-bit-ly-more-than-5-fall-deceived.html

ZAP. (s. f.-a). *Manipulator-in-the-middle proxy*. ZAP Documentation. https://www.zaproxy.org/docs/desktop/start/features/intercept/

ZAP. (s. f.-b). *ZAP downloads*. https://www.zaproxy.org/download/

**En el texto:** cambie las citas "(IEC Webstore, 2022a)" por "(ISO/IEC, 2022a)" y "(IEC Webstore, 2022b)" por "(ISO/IEC, 2022b)"; "(ZAP, s. f.)" por "(ZAP, s. f.-a)"; y "(Apache Software Foundation, s. f.)" por "(Apache Software Foundation, s. f.-a)".

---

## 18. Revisión final antes de exportar a PDF

- [ ] Título de la portada y del encabezado (punto 0).
- [ ] Sin notas internas: buscar "verifíquela", "deben contrastarse", "debe discutirse", "antes de entregar".
- [ ] Las tablas 6.2 y 6.3 se ven bien en el PDF (en el PDF actual, la extracción de texto sale desordenada; revise que no estén partidas entre páginas).
- [ ] Figuras 9 y 10: en las capturas de GitHub se lee "Marcelo Acuña and claude" como autores del commit. Decidan si las recortan.
- [ ] Si van a demostrar en vivo, ensayen la prueba del navegador **con la contraseña correcta durante el bloqueo**: en la Figura 8 no aparece ningún LOGIN_BLOCKED desde 172.22.0.1, así que esa prueba no se hizo desde el navegador.
