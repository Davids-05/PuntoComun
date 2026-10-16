"""Fixtures compartidas. Cada prueba usa una base SQLite en memoria nueva y limpia."""
import os

os.environ["SECRET_KEY"] = "clave-solo-para-pruebas-con-mas-de-32-caracteres"
os.environ["EMAIL_MODE"] = "console"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.middleware.rate_limit import limitador
from app.services import email_service


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sesion = sessionmaker(bind=engine, autoflush=False)()
    yield sesion
    sesion.close()


@pytest.fixture()
def correos(monkeypatch):
    """Captura los códigos OTP que se 'enviarían' por correo: lista de (destino, codigo)."""
    enviados = []
    monkeypatch.setattr(email_service, "enviar_codigo", lambda destino, codigo: enviados.append((destino, codigo)))
    return enviados


@pytest.fixture()
def client(db_session, correos):
    limitador.reiniciar()
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


DATOS = {"email": "ana@correo.co", "nombre": "Ana Pérez", "password": "Clave1234"}


@pytest.fixture()
def usuario_registrado(client):
    r = client.post("/auth/register", json=DATOS)
    assert r.status_code == 201
    return DATOS


@pytest.fixture()
def sesion_iniciada(client, usuario_registrado, correos):
    """Hace el flujo completo (contraseña + OTP) y devuelve el token."""
    client.post("/auth/login", json={"email": DATOS["email"], "password": DATOS["password"]})
    codigo = correos[-1][1]
    r = client.post("/auth/verify-otp", json={"email": DATOS["email"], "codigo": codigo})
    assert r.status_code == 200
    return r.json()["access_token"]
