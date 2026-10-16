"""Ciclo de vida del OTP: emitir y verificar (vence, tiene máximo de intentos y es de un solo uso)."""
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import CodigoOtp, Usuario
from app.security import otp as seguridad_otp
from app.services import email_service
from app.services.errors import ServicioError
from app.utils import ahora

MSG_INVALIDO = "Código inválido o vencido"


def emitir_otp(db: Session, usuario: Usuario) -> None:
    s = get_settings()
    # un solo código vigente por usuario: se invalidan los anteriores
    for previo in db.scalars(select(CodigoOtp).where(CodigoOtp.usuario_id == usuario.id, CodigoOtp.usado.is_(False))):
        previo.usado = True
    codigo = seguridad_otp.generar_codigo()
    db.add(CodigoOtp(usuario_id=usuario.id, codigo_hash=seguridad_otp.hash_codigo(codigo, usuario.id),
                     expira_en=ahora() + timedelta(minutes=s.otp_minutos)))
    db.commit()
    email_service.enviar_codigo(usuario.email, codigo)  # se envía después de guardar


def verificar_otp(db: Session, usuario: Usuario, codigo: str) -> None:
    s = get_settings()
    vigente = db.scalar(select(CodigoOtp).where(CodigoOtp.usuario_id == usuario.id, CodigoOtp.usado.is_(False))
                        .order_by(CodigoOtp.id.desc()))
    if vigente is None or vigente.expira_en < ahora():
        raise ServicioError(401, MSG_INVALIDO)
    if vigente.intentos >= s.otp_max_intentos:
        vigente.usado = True  # se quema el código; hay que pedir otro
        db.commit()
        raise ServicioError(429, "Demasiados intentos. Solicita un código nuevo.")
    if not seguridad_otp.coincide(codigo, usuario.id, vigente.codigo_hash):
        vigente.intentos += 1
        db.commit()
        raise ServicioError(401, MSG_INVALIDO)
    vigente.usado = True  # un solo uso
    db.commit()
