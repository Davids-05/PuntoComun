"""Limitador de peticiones por IP con ventana deslizante, en memoria.
Limitación conocida: funciona por proceso. Con varios procesos o servidores hay que moverlo a Redis."""
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from app.config import get_settings


class LimitadorMemoria:
    def __init__(self):
        self._eventos: dict[str, deque] = defaultdict(deque)

    def reiniciar(self) -> None:
        self._eventos.clear()

    def verificar(self, clave: str, limite: int, ventana: int) -> None:
        ahora = time.monotonic()
        cola = self._eventos[clave]
        while cola and ahora - cola[0] > ventana:
            cola.popleft()
        if len(cola) >= limite:
            espera = max(1, int(ventana - (ahora - cola[0])))
            raise HTTPException(429, "Demasiados intentos. Espera un momento e intenta de nuevo.",
                                headers={"Retry-After": str(espera)})
        cola.append(ahora)


limitador = LimitadorMemoria()


def _ip(request: Request) -> str:
    if get_settings().trust_proxy:
        reenviado = request.headers.get("x-forwarded-for")
        if reenviado:
            return reenviado.split(",")[0].strip()
    return request.client.host if request.client else "desconocida"


def limitar(nombre: str, attr_limite: str, attr_ventana: str):
    """Crea una dependencia: limitar('login', 'login_limit', 'login_window')."""
    def dependencia(request: Request) -> None:
        s = get_settings()
        limitador.verificar(f"{nombre}:{_ip(request)}", getattr(s, attr_limite), getattr(s, attr_ventana))
    return dependencia
