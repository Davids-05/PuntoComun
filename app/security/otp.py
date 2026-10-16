"""Generación y verificación de códigos OTP. Se guarda solo un HMAC del código, nunca el código."""
import hashlib
import hmac
import secrets

from app.config import get_settings


def generar_codigo() -> str:
    n = get_settings().otp_digitos
    return f"{secrets.randbelow(10 ** n):0{n}d}"  # aleatorio criptográfico, con ceros a la izquierda


def hash_codigo(codigo: str, usuario_id: int) -> str:
    clave = get_settings().secret_key.encode()
    return hmac.new(clave, f"{usuario_id}:{codigo}".encode(), hashlib.sha256).hexdigest()


def coincide(codigo: str, usuario_id: int, hash_guardado: str) -> bool:
    return hmac.compare_digest(hash_codigo(codigo, usuario_id), hash_guardado)  # tiempo constante
