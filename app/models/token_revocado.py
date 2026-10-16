from datetime import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TokenRevocado(Base):
    """Tokens cerrados con logout. Se guarda el jti hasta que el token expire."""
    __tablename__ = "tokens_revocados"

    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    expira_en: Mapped[datetime]
