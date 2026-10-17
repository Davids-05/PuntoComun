"""Configuración de la aplicación. Todo valor sensible viene de variables de entorno (.env)."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "gkP9mX2vR7bN5wQ1zT4yL8xK3jF6hG9pE"
    database_url: str = "sqlite:///./puntocomun.db"

    # JWT
    access_token_minutes: int = 30
    cookie_nombre: str = "pc_token"
    cookie_secure: bool = True  # True cuando se sirve por HTTPS

    # OTP
    otp_digitos: int = 6
    otp_minutos: int = 5
    otp_max_intentos: int = 5

    # Correo: "console" imprime el código (solo desarrollo); "smtp" envía correo por SMTP (producción); brevo para correo para vps gratuito
    email_mode: str = "brevo"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = "davisnavarroguzman@gmail.com"
    smtp_password: str = "isbiqxoenlkrhmuj"
    smtp_from: str = "no-reply@puntocomun.local"
    brevo_api_key: str = "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"
    email_remitente: str = "davisnavarroguzman@gmail.com"
    email_remitente_nombre: str = "PuntoComún"

    # Rate limiting (peticiones permitidas por ventana en segundos, por IP)
    login_limit: int = 5
    login_window: int = 60
    otp_limit: int = 5
    otp_window: int = 60
    resend_limit: int = 3
    resend_window: int = 300
    trust_proxy: bool = True  # True detrás de Render/Railway para leer X-Forwarded-For


@lru_cache
def get_settings() -> Settings:
    return Settings()
