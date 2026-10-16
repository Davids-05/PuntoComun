import jwt
import pytest

from app.models import CodigoOtp, Usuario
from app.security.tokens import crear_token
from tests.conftest import DATOS


def test_registro_exitoso_no_expone_la_contrasena(client, db_session):
    r = client.post("/auth/register", json=DATOS)
    assert r.status_code == 201
    assert "password" not in r.text and r.json()["email"] == DATOS["email"]
    guardado = db_session.query(Usuario).one()
    assert guardado.password_hash != DATOS["password"] and guardado.password_hash.startswith("$2")


def test_registro_duplicado_da_409(client, usuario_registrado):
    assert client.post("/auth/register", json=DATOS).status_code == 409


@pytest.mark.parametrize("cambio", [{"password": "corta1"}, {"password": "sololetrasaaa"}, {"password": "12345678"},
                                    {"email": "no-es-correo"}, {"nombre": "   "}])
def test_registro_invalido_da_422(client, cambio):
    assert client.post("/auth/register", json={**DATOS, **cambio}).status_code == 422


def test_login_con_clave_incorrecta_y_usuario_inexistente_responden_igual(client, usuario_registrado):
    a = client.post("/auth/login", json={"email": DATOS["email"], "password": "Incorrecta1"})
    b = client.post("/auth/login", json={"email": "nadie@correo.co", "password": "Incorrecta1"})
    assert a.status_code == b.status_code == 401 and a.json() == b.json()


def test_login_correcto_pide_otp_y_no_entrega_token(client, usuario_registrado, correos):
    r = client.post("/auth/login", json={"email": DATOS["email"], "password": DATOS["password"]})
    assert r.status_code == 200 and r.json()["otp_requerido"] is True
    assert "access_token" not in r.text and len(correos) == 1


def test_otp_incorrecto_da_401_y_correcto_entrega_token_y_cookie(client, usuario_registrado, correos):
    client.post("/auth/login", json={"email": DATOS["email"], "password": DATOS["password"]})
    codigo = correos[-1][1]
    malo = "000000" if codigo != "000000" else "111111"
    assert client.post("/auth/verify-otp", json={"email": DATOS["email"], "codigo": malo}).status_code == 401
    r = client.post("/auth/verify-otp", json={"email": DATOS["email"], "codigo": codigo})
    assert r.status_code == 200 and r.json()["access_token"]
    assert "pc_token" in client.cookies and "httponly" in r.headers["set-cookie"].lower()


def test_otp_con_formato_invalido_da_422(client, usuario_registrado):
    assert client.post("/auth/verify-otp", json={"email": DATOS["email"], "codigo": "12ab"}).status_code == 422


def test_ruta_protegida_sin_token_da_401_y_con_token_da_200(client, sesion_iniciada):
    client.cookies.clear()
    assert client.get("/auth/me").status_code == 401
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {sesion_iniciada}"})
    assert r.status_code == 200 and r.json()["email"] == DATOS["email"]


def test_la_cookie_tambien_autentica(client, sesion_iniciada):
    assert client.get("/auth/me").status_code == 200  # el cliente conservó la cookie


def test_logout_revoca_el_token(client, sesion_iniciada):
    cabecera = {"Authorization": f"Bearer {sesion_iniciada}"}
    assert client.post("/auth/logout", headers=cabecera).status_code == 204
    client.cookies.clear()
    r = client.get("/auth/me", headers=cabecera)
    assert r.status_code == 401


def test_token_vencido_da_401(client, usuario_registrado, db_session):
    usuario = db_session.query(Usuario).one()
    token, _, _ = crear_token(usuario.id, minutos=-1)
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401 and "expirada" in r.json()["detail"]


def test_token_con_firma_falsa_da_401(client, usuario_registrado):
    falso = jwt.encode({"sub": "1", "jti": "x", "exp": 9999999999}, "otra-clave", algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_rate_limit_en_login(client, usuario_registrado):
    estados = [client.post("/auth/login", json={"email": DATOS["email"], "password": "Incorrecta1"}).status_code
               for _ in range(7)]
    assert estados[:5] == [401] * 5 and estados[5] == 429


def test_rate_limit_en_reenvio_de_otp(client, usuario_registrado):
    estados = [client.post("/auth/resend-otp", json={"email": DATOS["email"]}).status_code for _ in range(4)]
    assert estados == [200, 200, 200, 429]


def test_reenvio_no_revela_si_el_correo_existe(client, usuario_registrado):
    a = client.post("/auth/resend-otp", json={"email": DATOS["email"]})
    b = client.post("/auth/resend-otp", json={"email": "nadie@correo.co"})
    assert a.json() == b.json()


def test_el_codigo_otp_no_se_guarda_en_claro(client, usuario_registrado, correos, db_session):
    client.post("/auth/login", json={"email": DATOS["email"], "password": DATOS["password"]})
    assert correos[-1][1] not in db_session.query(CodigoOtp).one().codigo_hash


def test_cabeceras_de_seguridad(client):
    r = client.get("/health")
    assert r.headers["x-content-type-options"] == "nosniff" and r.headers["x-frame-options"] == "DENY"
