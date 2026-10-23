"""Configuración de la aplicación. Todo valor sensible viene de variables de entorno (.env)."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "cambia-esta-clave-solo-para-desarrollo"
    database_url: str = "sqlite:///./puntocomun.db"

    # JWT
    access_token_minutes: int = 30
    cookie_nombre: str = "pc_token"
    cookie_secure: bool = False  # True cuando se sirve por HTTPS

    # OTP
    otp_digitos: int = 6
    otp_minutos: int = 5
    otp_max_intentos: int = 5

    # Correo: "console" imprime el código (solo desarrollo); "smtp" envía de verdad
    email_mode: str = "console"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-reply@puntocomun.local"

    # Rate limiting (peticiones permitidas por ventana en segundos, por IP)
    login_limit: int = 5
    login_window: int = 60
    otp_limit: int = 5
    otp_window: int = 60
    resend_limit: int = 3
    resend_window: int = 300
    trust_proxy: bool = False  


@lru_cache
def get_settings() -> Settings:
    return Settings()
