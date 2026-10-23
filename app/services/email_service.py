import logging
import smtplib
import httpx
from pydantic import SecretStr
import os
from app.config import get_settings
from app.services.errors import ServicioError

log = logging.getLogger("puntocomun.email")

URL_BREVO = "https://api.brevo.com/v3/smtp/email"
MSG_FALLO = "No pudimos enviar el código. Intenta de nuevo en unos minutos."

def _enviar_brevo(destino: str, asunto: str, texto: str, html: str) -> None:
    """Envía un correo usando la API HTTP nativa de Brevo (Puerto 443)."""
    s = get_settings()
    
    # Extraemos la clave API. Asegúrate de tener BREVO_API_KEY en tu .env o en Render.
    api_key = os.getenv("BREVO_API_KEY") 
    
    if not api_key:
        log.error("Falta BREVO_API_KEY en las variables de entorno.")
        raise ServicioError(500, MSG_FALLO)

    # Construimos el cuerpo JSON requerido por Brevo
    payload = {
        "sender": {"name": s.email_remitente_nombre, "email": s.email_remitente},
        "to": [{"email": destino}],
        "subject": asunto,
        "htmlContent": html,
        "textContent": texto
    }

    # Configuramos los headers
    headers = {
        "api-key": api_key,
        "accept": "application/json",
        "content-type": "application/json"
    }

    try:
        # Hacemos la petición POST directamente a la API de Brevo
        r = httpx.post(URL_BREVO, timeout=10, headers=headers, json=payload)
        
        # Validamos si Brevo nos devolvió un error (ej. clave inválida, saldo agotado)
        r.raise_for_status()
        
        # Si el código de respuesta es 201 (Created), el correo fue puesto en cola con éxito.
        log.info(f"Correo enviado exitosamente vía Brevo API a {destino}")
        
    except httpx.HTTPStatusError as e:
        log.error("Brevo API rechazó el envío. Status: %s, Detalle: %s", e.response.status_code, e.response.text)
        raise ServicioError(503, MSG_FALLO)
    except httpx.RequestError as e:
        log.error("Error de conexión al intentar alcanzar la API de Brevo: %s", type(e).__name__)
        raise ServicioError(503, MSG_FALLO)

def _enviar_smtp(destino: str, asunto: str, texto: str) -> None:
    s = get_settings()
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = asunto, s.email_remitente or s.smtp_from, destino
    msg.set_content(texto)
    try:
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(s.smtp_user, s.smtp_password)
            smtp.send_message(msg)
    except Exception:
        log.exception("Falló el envío por SMTP")  # el log no incluye el código
        raise ServicioError(503, MSG_FALLO)


    
def enviar_codigo(destino: str, codigo: str) -> None:
    """Función principal para enrutar el envío del OTP."""
    s = get_settings()
    
    asunto = "Código de verificación de PuntoComún"
    texto = f"Tu código de acceso es: {codigo}. Vence en {s.otp_minutos} minutos."
    html = f"""
    <div style="font-family: Arial, sans-serif; text-align: center; color: #333;">
        <h2>Ingreso a PuntoComún</h2>
        <p>Tu código de seguridad para iniciar sesión es:</p>
        <h1 style="color: #007BFF; letter-spacing: 5px;">{codigo}</h1>
        <p>Este código expira en {s.otp_minutos} minutos. No lo compartas con nadie.</p>
    </div>
    """

    # Modo Consola (Para pruebas locales o cuando no quieres gastar correos)
    if s.email_mode == "console":
        log.warning("[SOLO DESARROLLO] Código OTP para %s: %s", destino, codigo)
        return

    # Modo Brevo (Para Producción en Render)
    if s.email_mode == "brevo":
        _enviar_brevo(destino, asunto, texto, html)
        return
    
    elif s.email_mode == "smtp":
        _enviar_smtp(destino, asunto, texto)
        return
    
    print("EMAIL_MODE:", s.email_mode)
    # Si se detecta un modo no soportado o "smtp"
    log.error("EMAIL_MODE desconocido o no soportado en producción: %s", s.email_mode)
    raise ServicioError(503, MSG_FALLO)
