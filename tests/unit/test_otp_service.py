from datetime import timedelta
import pytest

from app.models import CodigoOtp, Usuario
from app.services import otp_service
from app.services.errors import ServicioError
from app.utils import ahora


@pytest.fixture()
def usuario(db_session):
    u = Usuario(email="a@correo.co", nombre="A", password_hash="x")
    db_session.add(u)
    db_session.commit()
    return u


def test_codigo_correcto_funciona_una_sola_vez(db_session, usuario, correos):
    otp_service.emitir_otp(db_session, usuario)
    codigo = correos[-1][1]
    otp_service.verificar_otp(db_session, usuario, codigo)
    with pytest.raises(ServicioError) as e:
        otp_service.verificar_otp(db_session, usuario, codigo)
    assert e.value.status_code == 401


def test_codigo_vencido_se_rechaza(db_session, usuario, correos):
    otp_service.emitir_otp(db_session, usuario)
    registro = db_session.query(CodigoOtp).one()
    registro.expira_en = ahora() - timedelta(seconds=1)
    db_session.commit()
    with pytest.raises(ServicioError) as e:
        otp_service.verificar_otp(db_session, usuario, correos[-1][1])
    assert e.value.status_code == 401


def test_intentos_agotados_bloquea_incluso_el_codigo_correcto(db_session, usuario, correos):
    otp_service.emitir_otp(db_session, usuario)
    correcto = correos[-1][1]
    malo = "000000" if correcto != "000000" else "111111"
    for _ in range(5):
        with pytest.raises(ServicioError) as e:
            otp_service.verificar_otp(db_session, usuario, malo)
        assert e.value.status_code == 401
    with pytest.raises(ServicioError) as e:
        otp_service.verificar_otp(db_session, usuario, correcto)
    assert e.value.status_code == 429


def test_un_codigo_nuevo_invalida_el_anterior(db_session, usuario, correos):
    otp_service.emitir_otp(db_session, usuario)
    viejo = correos[-1][1]
    otp_service.emitir_otp(db_session, usuario)
    nuevo = correos[-1][1]
    if viejo != nuevo:
        with pytest.raises(ServicioError):
            otp_service.verificar_otp(db_session, usuario, viejo)
    otp_service.verificar_otp(db_session, usuario, nuevo)
