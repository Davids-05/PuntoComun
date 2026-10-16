from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Categoria = Literal["vias", "alumbrado", "agua", "espacios_publicos"]


class ReporteIn(BaseModel):
    categoria: Categoria
    descripcion: str = Field(min_length=5, max_length=500)
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)


class ReporteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    categoria: str
    descripcion: str
    latitud: float
    longitud: float
    estado: str
    creado_en: datetime
