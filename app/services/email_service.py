"""Envío del OTP por correo. En desarrollo imprime el código en el log; en producción usa SMTP."""
import logging
import smtplib
from email.message import EmailMessage

from app.config import get_settings
from app.services.errors import ServicioError

log = logging.getLogger("puntocomun.email")


def enviar_codigo(destino: str, codigo: str) -> None:
    s = get_settings()
    if s.email_mode == "console":
        log.warning("[SOLO DESARROLLO] Código OTP para %s: %s", destino, codigo)
        return
    msg = EmailMessage()
    msg["Subject"] = "Tu código de verificación de PuntoComún"
    msg["From"] = s.smtp_from
    msg["To"] = destino
    msg.set_content(f"Tu código es {codigo}. Vence en {s.otp_minutos} minutos. "
                    "Si no lo pediste, ignora este mensaje.")
    try:
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(s.smtp_user, s.smtp_password)
            smtp.send_message(msg)
    except Exception:
        log.exception("Falló el envío del correo")  # el log no incluye el código
        raise ServicioError(503, "No pudimos enviar el código. Intenta de nuevo en unos minutos.")
