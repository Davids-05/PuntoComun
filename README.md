# PuntoComún: autenticación con OTP (FastAPI)

Plataforma web de reportes de daños en infraestructura. Esta primera versión implementa el sistema de acceso:
registro, inicio de sesión en dos pasos (contraseña y código OTP por correo), JWT, rutas protegidas y cierre de sesión,
más un módulo básico de reportes para demostrar las rutas protegidas.

**Tecnología:** FastAPI, SQLAlchemy 2, SQLite, bcrypt, PyJWT, frontend en HTML, JS y CSS simples, pytest.

## Cómo ejecutarlo (Windows, PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # edita SECRET_KEY: una clave aleatoria de 32 caracteres o más
uvicorn app.main:app --reload
```

- Aplicación: http://localhost:8000
- Documentación interactiva de la API: http://localhost:8000/docs
- Con `EMAIL_MODE=console` el código OTP **se imprime en la consola** donde corre uvicorn (solo desarrollo).

## Pruebas

```powershell
pytest
```

35 pruebas: unitarias (hash, JWT, OTP, vencimiento, intentos) e integración (flujo completo, 401, 409, 422, 429, logout, cookie).

## Estructura

```
app/
  main.py          crea la app, errores, cabeceras de seguridad y sirve el frontend
  config.py        variables de entorno (.env)
  database.py      conexión y sesión de SQLAlchemy
  models/          usuarios, codigos_otp, tokens_revocados, reportes
  schemas/         validación de entradas y salidas (Pydantic)
  routes/          URLs: auth_routes.py, reporte_routes.py
  controllers/     orquestan cada operación
  services/        lógica: cuentas, OTP, correo
  middleware/      auth_jwt.py (rutas protegidas) y rate_limit.py
  security/        passwords.py (bcrypt), tokens.py (JWT), otp.py
frontend/          index, registro, ingreso (2 pasos), reportar
tests/             unit/ e integration/
docs/              guia_sustentacion.md
```

## Flujo de autenticación

1. `POST /auth/register`: crea la cuenta (la contraseña se guarda con hash bcrypt).
2. `POST /auth/login`: valida correo y contraseña y envía un OTP de 6 dígitos por correo. Todavía no entrega token.
3. `POST /auth/verify-otp`: valida el OTP y entrega el JWT (también como cookie HttpOnly).
4. Rutas protegidas: aceptan el JWT por cabecera `Authorization: Bearer ...` o por la cookie.
5. `POST /auth/logout`: revoca el token (su `jti` queda en la tabla `tokens_revocados`).

| Método y ruta | Acceso | Respuestas |
|---|---|---|
| POST /auth/register | público | 201, 409 (correo repetido), 422 |
| POST /auth/login | público, límite por IP | 200, 401, 422, 429 |
| POST /auth/verify-otp | público, límite por IP | 200, 401, 422, 429 |
| POST /auth/resend-otp | público, límite por IP | 200, 422, 429 |
| POST /auth/logout | protegido | 204, 401 |
| GET /auth/me | protegido | 200, 401 |
| GET /reportes | público | 200 |
| POST /reportes | protegido | 201, 401, 422 |
| GET /health | público | 200 |

## Decisiones de seguridad

- **Contraseñas:** bcrypt con sal aleatoria; mínimo 8 caracteres con letra y número; nunca se devuelven ni se registran.
- **Login sin pistas:** correo inexistente y contraseña incorrecta dan la misma respuesta y se compara contra un hash de relleno para que tarde parecido.
- **OTP:** 6 dígitos con `secrets`; se guarda solo un HMAC del código; vence a los 5 minutos; máximo 5 intentos; un solo uso; un código nuevo invalida el anterior.
- **JWT:** HS256 con `exp`, `jti` e `iat`; vence a los 30 minutos; se rechazan tokens vencidos, manipulados o revocados.
- **Cookie:** HttpOnly, SameSite=Strict y Secure en producción (mitiga robo por XSS y CSRF).
- **Rate limiting:** por IP en login (5 por minuto), verificación de OTP (5 por minuto) y reenvío (3 cada 5 minutos).
- **Cabeceras:** `nosniff`, `X-Frame-Options`, `Content-Security-Policy` y `Referrer-Policy`.
- **Frontend:** todo texto se pinta con `textContent`, nunca con `innerHTML`.
- **Secretos:** solo en variables de entorno; el arranque en producción falla si la clave es débil.

## Limitaciones conocidas (honestas)

- El limitador de peticiones vive en la memoria de un proceso: con varios procesos o servidores hay que usar Redis.
- `create_all` crea las tablas al arrancar; en un proyecto real se usarían migraciones (Alembic).
- El registro revela si un correo ya existe (409). Es una decisión de usabilidad; el login y el reenvío no lo revelan.
- Aún no hay verificación del correo al registrarse, recuperación de contraseña ni roles institucionales con panel.
- Se probó el envío SMTP real: hay que verificarlo en producción debido a las leyes anti-spam de algunos vos gratuitos.
