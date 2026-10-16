"""Protección de rutas: lee el JWT (encabezado Bearer o cookie), lo valida y carga al usuario."""
from dataclasses import dataclass
from datetime import datetime, timezone

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Usuario
from app.security.tokens import decodificar_token
from app.services.auth_service import token_revocado

_bearer = HTTPBearer(auto_error=False)


@dataclass
class Sesion:
    usuario: Usuario
    jti: str
    expira_en: datetime


def sesion_actual(request: Request, cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
                  db: Session = Depends(get_db)) -> Sesion:
    token = cred.credentials if cred else request.cookies.get(get_settings().cookie_nombre)
    if not token:
        raise HTTPException(401, "No autenticado")
    try:
        claims = decodificar_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Sesión expirada")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token inválido")
    if token_revocado(db, claims["jti"]):
        raise HTTPException(401, "Sesión cerrada")
    usuario = db.get(Usuario, int(claims["sub"]))
    if not usuario or not usuario.activo:
        raise HTTPException(401, "Token inválido")
    return Sesion(usuario, claims["jti"], datetime.fromtimestamp(claims["exp"], tz=timezone.utc))


def usuario_actual(sesion: Sesion = Depends(sesion_actual)) -> Usuario:
    return sesion.usuario


def requiere_rol(*roles: str):
    """Para rutas que solo ciertos roles pueden usar (por ejemplo, institucional o admin)."""
    def dependencia(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(403, "No tienes permiso para esta acción")
        return usuario
    return dependencia
