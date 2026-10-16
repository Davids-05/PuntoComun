"""JWT de acceso: HS256 con expiración (exp) e identificador único (jti) para poder revocarlo."""
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.config import get_settings

ALGORITMO = "HS256"


def crear_token(usuario_id: int, minutos: int | None = None) -> tuple[str, str, datetime]:
    s = get_settings()
    minutos = s.access_token_minutes if minutos is None else minutos
    ahora = datetime.now(timezone.utc)
    exp = ahora + timedelta(minutes=minutos)
    jti = uuid.uuid4().hex
    payload = {"sub": str(usuario_id), "jti": jti, "iat": ahora, "exp": exp}
    return jwt.encode(payload, s.secret_key, algorithm=ALGORITMO), jti, exp


def decodificar_token(token: str) -> dict:
    """Lanza jwt.ExpiredSignatureError o jwt.InvalidTokenError si el token no es válido."""
    return jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITMO],
                      options={"require": ["exp", "sub", "jti"]})
