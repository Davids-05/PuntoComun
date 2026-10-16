from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.utils import ahora


class Reporte(Base):
    __tablename__ = "reportes"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    categoria: Mapped[str] = mapped_column(String(30))
    descripcion: Mapped[str] = mapped_column(String(500))
    latitud: Mapped[float]
    longitud: Mapped[float]
    estado: Mapped[str] = mapped_column(String(20), default="reportado")
    creado_en: Mapped[datetime] = mapped_column(default=ahora)
