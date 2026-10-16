"""Lógica de cuentas: registro, autenticación con contraseña y revocación de tokens."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import TokenRevocado, Usuario
from app.schemas.auth import RegistroIn
from app.security.passwords import hashear, verificar
from app.services.errors import ServicioError
from app.utils import ahora


def buscar_por_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email))


def registrar_usuario(db: Session, datos: RegistroIn) -> Usuario:
    if buscar_por_email(db, datos.email):
        raise ServicioError(409, "El correo ya está registrado")
    usuario = Usuario(email=datos.email, nombre=datos.nombre, password_hash=hashear(datos.password))
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:  # dos registros simultáneos con el mismo correo
        db.rollback()
        raise ServicioError(409, "El correo ya está registrado")
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, email: str, password: str) -> Usuario:
    """Paso 1 del login. Misma respuesta si el correo no existe o la contraseña es incorrecta."""
    usuario = buscar_por_email(db, email)
    ok = verificar(password, usuario.password_hash if usuario else None)
    if not usuario or not ok or not usuario.activo:
        raise ServicioError(401, "Credenciales inválidas")
    return usuario


def revocar_token(db: Session, jti: str, expira_en: datetime) -> None:
    if not db.get(TokenRevocado, jti):
        db.add(TokenRevocado(jti=jti, expira_en=expira_en.replace(tzinfo=None)))
        db.commit()
    db.query(TokenRevocado).filter(TokenRevocado.expira_en < ahora()).delete()  # limpieza de vencidos
    db.commit()


def token_revocado(db: Session, jti: str) -> bool:
    return db.get(TokenRevocado, jti) is not None
