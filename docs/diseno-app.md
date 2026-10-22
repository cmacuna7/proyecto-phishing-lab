# Diseño de la aplicación

## Diagrama de secuencia (UML, Mermaid)

```mermaid
sequenceDiagram
  actor U as Usuario
  participant P as Apache/NGINX
  participant A as App Flask
  participant D as SQLite
  participant L as auth.log
  U->>P: GET /r/qr1
  P->>A: GET /r/qr1
  A->>L: LINK_VISIT
  A-->>U: 302 /login?ref=qr1
  U->>P: POST /login (usuario, clave)
  P->>A: POST /login (X-Forwarded-For)
  A->>D: ¿cuenta bloqueada?
  alt bloqueada
    A->>L: LOGIN_BLOCKED
    A-->>U: 429 + Retry-After
  else clave incorrecta
    A->>D: failed_count + 1
    A->>L: LOGIN_FAILED (y LOCKOUT_START al 3.º)
    A-->>U: 401 (mensaje informativo)
  else clave correcta
    A->>D: reiniciar contador
    A->>L: LOGIN_SUCCESS
    A-->>U: 302 /panel
  end
```

## Reglas
- Bloqueo tras 3 fallos **consecutivos**; dura 120 s; la contraseña correcta se rechaza durante el bloqueo.
- Éxito reinicia el contador. Fin del bloqueo se registra como `LOCKOUT_END`.
- Respuestas genéricas: no revelan si el usuario existe.
- Registro JSON Lines con lista cerrada de campos: no existe campo para contraseñas.
- Códigos: 401 fallo, 429 bloqueo, 302 éxito.
