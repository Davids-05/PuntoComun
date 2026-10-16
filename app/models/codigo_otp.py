from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.utils import ahora


class CodigoOtp(Base):
    __tablename__ = "codigos_otp"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    codigo_hash: Mapped[str] = mapped_column(String(64))  # HMAC del código, no el código
    expira_en: Mapped[datetime]
    intentos: Mapped[int] = mapped_column(default=0)
    usado: Mapped[bool] = mapped_column(default=False)
    creado_en: Mapped[datetime] = mapped_column(default=ahora)
