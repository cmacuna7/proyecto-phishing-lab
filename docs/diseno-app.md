# Diseño de la aplicación

## Diagrama de secuencia (UML, Mermaid)

Modo `hardened` (con controles). En `baseline` no hay bloqueo ni escritura en `auth.log`.
Se puede renderizar en https://mermaid.live o en la vista previa de Markdown de VS Code/GitHub.

```mermaid
sequenceDiagram
  actor U as Usuario
  participant P as Apache / NGINX
  participant A as Aplicación Flask
  participant D as SQLite (users)
  participant L as auth.log
  participant S as Hilo de barrido

  U->>P: GET /r/qr1
  P->>A: GET /r/qr1 (X-Forwarded-For)
  A->>L: LINK_VISIT (ref=afiche-qr)
  A-->>U: 302 /login?ref=afiche-qr
  U->>P: POST /login (usuario, contraseña)
  P->>A: POST /login (X-Forwarded-For)
  A->>D: BEGIN IMMEDIATE · leer failed_count, locked_until
  alt cuenta bloqueada (ahora < locked_until)
    A->>L: LOGIN_BLOCKED
    A-->>U: 429 + Retry-After (no se evalúa la contraseña)
  else cuenta no bloqueada
    A->>A: validar credenciales (PBKDF2 + comparación en tiempo constante)
    alt contraseña correcta
      A->>D: failed_count = 0
      A->>L: LOGIN_SUCCESS
      A-->>U: 302 /panel
    else contraseña incorrecta
      A->>D: failed_count + 1
      A->>L: LOGIN_FAILED
      opt failed_count = 3
        A->>D: locked_until = ahora + 120 s
        A->>L: LOCKOUT_START
      end
      A-->>U: 401 (al 3.er fallo, con mensaje de bloqueo)
    end
  end
  loop cada 1 s
    S->>D: ¿bloqueos vencidos?
    opt locked_until <= ahora
      S->>D: failed_count = 0, locked_until = NULL
      S->>L: LOCKOUT_END (hora = locked_until)
    end
  end
```

## Reglas
- Bloqueo tras 3 fallos **consecutivos**; dura 120 s; la contraseña correcta se rechaza durante el bloqueo.
- Éxito reinicia el contador. El fin del bloqueo se registra como `LOCKOUT_END` con la hora programada de fin.
- El mensaje de error es genérico, pero los usuarios inexistentes nunca se bloquean: una cuenta que responde 429 tras tres fallos existe (enumeración posible).
- Registro JSON Lines con lista cerrada de campos: no existe campo para contraseñas.
- Códigos: 401 fallo, 429 bloqueo, 302 éxito.
