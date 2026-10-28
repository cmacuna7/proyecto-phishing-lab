# Mensaje de phishing SIMULADO (solo laboratorio)

> **Condición de la práctica:** el enlace y el QR apuntan **exclusivamente** a la aplicación del
> laboratorio (`apache` / `nginx`). No se envía a personas externas, no se usan cuentas reales y
> no existe ningún sitio externo de captura de credenciales.

## Versión correo (para mostrar en el equipo de usuario 1)

**De:** Soporte TI <soporte@correo.lab.local> *(remitente ficticio)*
**Para:** usuario.demo@correo.lab.local
**Asunto:** Acción requerida: verifique su cuenta antes de las 18:00

Estimado usuario:

Detectamos un acceso inusual a su cuenta. Para evitar la suspensión del servicio, verifique sus
datos en el siguiente enlace:

**http://apache/r/mail1**

Si no confirma en las próximas horas, su cuenta será bloqueada.

Atentamente,
Equipo de Soporte

### Señales de alerta que se pueden señalar en la demostración

- Urgencia y amenaza de bloqueo.
- Remitente genérico y dominio que no coincide con el de la institución.
- Enlace corto (`/r/mail1`) que oculta el destino real.
- Saludo genérico, sin nombre.

## Versión afiche con código QR

Texto sugerido: *"Escanee para actualizar su contraseña institucional"*.
El QR se genera con `make qr` (o `python scripts/make_qr.py http://apache/r/qr1`) y apunta a
`http://apache/r/qr1`, que redirige solo a `/login` de la app del laboratorio.

## Abrir el enlace o el QR desde el navegador del anfitrión

`http://apache/...` y `http://nginx/...` son nombres internos de la red de Docker: solo funcionan
desde los contenedores `client1` y `client2`. Desde el navegador de Windows use el puerto publicado:

| Destino | Apache | NGINX |
|---|---|---|
| Enlace del correo | http://127.0.0.1:8081/r/mail1 | http://127.0.0.1:8082/r/mail1 |
| Enlace del QR | http://127.0.0.1:8081/r/qr1 | http://127.0.0.1:8082/r/qr1 |
| Imagen del QR | `qr_apache_navegador.png` | `qr_nginx_navegador.png` |

Un teléfono no puede abrir estos QR: `127.0.0.1` es el propio dispositivo que escanea y los
puertos solo están publicados en el anfitrión. Para la demostración, muestre el QR y abra el
enlace en el navegador del computador.

## Qué registra el laboratorio cuando alguien abre el enlace

`/r/mail1` y `/r/qr1` registran un evento `LINK_VISIT` con la campaña (`ref`) en el registro de
auditoría, y redirigen a `/login?ref=...`. Solo se aceptan esos dos códigos fijos: no existe redirección
abierta hacia otros sitios.
