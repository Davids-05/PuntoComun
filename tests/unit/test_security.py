import time
import jwt
import pytest

from app.security import otp
from app.security.passwords import hashear, verificar
from app.security.tokens import crear_token, decodificar_token


def test_hash_no_es_la_contrasena_y_verifica():
    h = hashear("Clave1234")
    assert h != "Clave1234" and h.startswith("$2")
    assert verificar("Clave1234", h)
    assert not verificar("otra-clave", h)


def test_dos_hashes_de_la_misma_clave_son_distintos():
    assert hashear("Clave1234") != hashear("Clave1234")  # sal aleatoria


def test_verificar_sin_usuario_devuelve_falso():
    assert verificar("cualquiera", None) is False


def test_token_contiene_sub_jti_y_expira():
    token, jti, _ = crear_token(7)
    claims = decodificar_token(token)
    assert claims["sub"] == "7" and claims["jti"] == jti


def test_token_vencido_se_rechaza():
    token, _, _ = crear_token(7, minutos=-1)
    with pytest.raises(jwt.ExpiredSignatureError):
        decodificar_token(token)


def test_token_manipulado_se_rechaza():
    token, _, _ = crear_token(7)
    with pytest.raises(jwt.InvalidTokenError):
        decodificar_token(token[:-2] + "xx")


def test_otp_tiene_seis_digitos_y_no_se_guarda_en_claro():
    codigo = otp.generar_codigo()
    assert len(codigo) == 6 and codigo.isdigit()
    h = otp.hash_codigo(codigo, 1)
    assert codigo not in h and otp.coincide(codigo, 1, h)
    assert not otp.coincide(codigo, 2, h)  # atado al usuario
