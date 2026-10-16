from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Reporte, Usuario
from app.schemas.reporte import ReporteIn


def crear(db: Session, usuario: Usuario, datos: ReporteIn) -> Reporte:
    reporte = Reporte(usuario_id=usuario.id, **datos.model_dump())
    db.add(reporte)
    db.commit()
    db.refresh(reporte)
    return reporte


def listar(db: Session, limite: int) -> list[Reporte]:
    return list(db.scalars(select(Reporte).order_by(Reporte.id.desc()).limit(limite)))
