"""Punto de entrada: crea la app, registra rutas, errores, cabeceras de seguridad y el frontend."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401  (registra las tablas)
from app.config import get_settings
from app.database import Base, engine
from app.routes import auth_routes, reporte_routes
from app.services.errors import ServicioError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
CLAVE_POR_DEFECTO = "cambia-esta-clave-solo-para-desarrollo"


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    if s.app_env == "production" and (s.secret_key == CLAVE_POR_DEFECTO or len(s.secret_key) < 32):
        raise RuntimeError("SECRET_KEY insegura: define una clave aleatoria de al menos 32 caracteres")
    Base.metadata.create_all(engine)  # para el parcial; en un proyecto real se usan migraciones (Alembic)
    yield


app = FastAPI(title="PuntoComún API", version="0.1.0", lifespan=lifespan)


@app.exception_handler(ServicioError)
async def manejar_servicio_error(request: Request, exc: ServicioError):
    return JSONResponse({"detail": exc.detalle}, status_code=exc.status_code)


@app.middleware("http")
async def cabeceras_seguridad(request: Request, call_next):
    respuesta = await call_next(request)
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "DENY"
    respuesta.headers["Referrer-Policy"] = "same-origin"
    if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):  # Swagger carga recursos externos
        respuesta.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
    return respuesta


app.include_router(auth_routes.router)
app.include_router(reporte_routes.router)


@app.get("/health", tags=["Operación"])
def health():
    return {"status": "ok"}


FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND.exists():  # se monta al final: las rutas de la API tienen prioridad
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
