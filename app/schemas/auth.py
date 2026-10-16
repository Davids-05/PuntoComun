"""Validación de entradas y salidas con Pydantic. Se rechaza lo inválido antes de tocar la base."""
import re
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _normalizar_email(v: str) -> str:
    return v.strip().lower()


class RegistroIn(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=64)

    @field_validator("email")
    @classmethod
    def email_minuscula(cls, v):
        return _normalizar_email(v)

    @field_validator("nombre")
    @classmethod
    def nombre_limpio(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v

    @field_validator("password")
    @classmethod
    def password_fuerte(cls, v):
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("La contraseña debe tener al menos una letra y un número")
        if len(v.encode()) > 72:  # límite técnico de bcrypt
            raise ValueError("La contraseña es demasiado larga")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=64)

    @field_validator("email")
    @classmethod
    def email_minuscula(cls, v):
        return _normalizar_email(v)


class VerificarOtpIn(BaseModel):
    email: EmailStr
    codigo: str = Field(pattern=r"^\d{6}$")

    @field_validator("email")
    @classmethod
    def email_minuscula(cls, v):
        return _normalizar_email(v)


class ReenviarOtpIn(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def email_minuscula(cls, v):
        return _normalizar_email(v)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    nombre: str
    rol: str


class MensajeOut(BaseModel):
    mensaje: str
    otp_requerido: bool = False


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_en_minutos: int
    usuario: UsuarioOut
