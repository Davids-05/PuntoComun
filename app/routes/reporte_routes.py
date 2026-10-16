from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.controllers import reporte_controller
from app.database import get_db
from app.middleware.auth_jwt import usuario_actual
from app.models import Usuario
from app.schemas.reporte import ReporteIn, ReporteOut

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("", response_model=list[ReporteOut])
def listar(limite: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    """Lectura pública: cualquiera puede ver el mapa de reportes."""
    return reporte_controller.listar(db, limite)


@router.post("", response_model=ReporteOut, status_code=201)
def crear(datos: ReporteIn, usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    """Ruta protegida: hace falta sesión iniciada con OTP."""
    return reporte_controller.crear(db, usuario, datos)
