"""URLs de autenticación. Cada ruta solo valida la entrada, aplica límites y delega al controlador."""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.config import get_settings
from app.controllers import auth_controller
from app.database import get_db
from app.middleware.auth_jwt import Sesion, sesion_actual
from app.middleware.rate_limit import limitar
from app.schemas.auth import (LoginIn, MensajeOut, RegistroIn, ReenviarOtpIn, TokenOut, UsuarioOut, VerificarOtpIn)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioOut, status_code=201)
def registrar(datos: RegistroIn, db: Session = Depends(get_db)):
    return auth_controller.registrar(db, datos)


@router.post("/login", response_model=MensajeOut,
             dependencies=[Depends(limitar("login", "login_limit", "login_window"))])
def login(datos: LoginIn, db: Session = Depends(get_db)):
    return auth_controller.iniciar_sesion(db, datos)


@router.post("/verify-otp", response_model=TokenOut,
             dependencies=[Depends(limitar("otp", "otp_limit", "otp_window"))])
def verificar_otp(datos: VerificarOtpIn, response: Response, db: Session = Depends(get_db)):
    resultado = auth_controller.verificar_otp(db, datos)
    s = get_settings()
    response.set_cookie(s.cookie_nombre, resultado.access_token, max_age=s.access_token_minutes * 60,
                        httponly=True, samesite="strict", secure=s.cookie_secure, path="/")
    return resultado


@router.post("/resend-otp", response_model=MensajeOut,
             dependencies=[Depends(limitar("resend", "resend_limit", "resend_window"))])
def reenviar_otp(datos: ReenviarOtpIn, db: Session = Depends(get_db)):
    return auth_controller.reenviar_otp(db, datos)


@router.post("/logout", status_code=204)
def logout(response: Response, sesion: Sesion = Depends(sesion_actual), db: Session = Depends(get_db)):
    auth_controller.cerrar_sesion(db, sesion)
    response.delete_cookie(get_settings().cookie_nombre, path="/")


@router.get("/me", response_model=UsuarioOut)
def yo(sesion: Sesion = Depends(sesion_actual)):
    return sesion.usuario
