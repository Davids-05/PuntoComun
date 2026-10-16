class ServicioError(Exception):
    """Error de negocio con código HTTP. main.py lo convierte en una respuesta JSON."""

    def __init__(self, status_code: int, detalle: str):
        self.status_code = status_code
        self.detalle = detalle
        super().__init__(detalle)
