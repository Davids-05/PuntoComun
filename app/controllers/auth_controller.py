"""Controladores de autenticación: reciben datos ya validados y orquestan los servicios."""
from sqlalchemy.orm import Session

from app.config import get_settings
from app.middleware.auth_jwt import Sesion
from app.schemas.auth import (LoginIn, MensajeOut, RegistroIn, ReenviarOtpIn, TokenOut, UsuarioOut, VerificarOtpIn)
from app.security.tokens import crear_token
from app.services import auth_service, otp_service
from app.services.errors import ServicioError

MSG_OTP_ENVIADO = "Si los datos son correctos, te enviamos un código a tu correo."


def registrar(db: Session, datos: RegistroIn) -> UsuarioOut:
    return UsuarioOut.model_validate(auth_service.registrar_usuario(db, datos))


def iniciar_sesion(db: Session, datos: LoginIn) -> MensajeOut:
    """Paso 1: contraseña correcta -> se envía el OTP. Todavía no hay token."""
    usuario = auth_service.autenticar(db, datos.email, datos.password)
    otp_service.emitir_otp(db, usuario)
    return MensajeOut(mensaje=MSG_OTP_ENVIADO, otp_requerido=True)


def verificar_otp(db: Session, datos: VerificarOtpIn) -> TokenOut:
    """Paso 2: OTP correcto -> se emite el JWT."""
    usuario = auth_service.buscar_por_email(db, datos.email)
    if not usuario or not usuario.activo:
        raise ServicioError(401, otp_service.MSG_INVALIDO)
    otp_service.verificar_otp(db, usuario, datos.codigo)
    token, _, _ = crear_token(usuario.id)
    return TokenOut(access_token=token, expira_en_minutos=get_settings().access_token_minutes,
                    usuario=UsuarioOut.model_validate(usuario))


def reenviar_otp(db: Session, datos: ReenviarOtpIn) -> MensajeOut:
    usuario = auth_service.buscar_por_email(db, datos.email)
    if usuario and usuario.activo:
        otp_service.emitir_otp(db, usuario)
    return MensajeOut(mensaje=MSG_OTP_ENVIADO, otp_requerido=True)  # misma respuesta exista o no el correo


def cerrar_sesion(db: Session, sesion: Sesion) -> None:
    auth_service.revocar_token(db, sesion.jti, sesion.expira_en)
