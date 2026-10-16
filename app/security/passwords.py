"""Hash de contraseñas con bcrypt (sal aleatoria incluida en cada hash)."""
import bcrypt

# Hash de relleno: se compara cuando el usuario no existe, para que la respuesta tarde parecido
_HASH_RELLENO = bcrypt.hashpw(b"relleno-no-es-una-clave", bcrypt.gensalt())


def hashear(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar(password: str, hash_guardado: str | None) -> bool:
    objetivo = hash_guardado.encode() if hash_guardado else _HASH_RELLENO
    ok = bcrypt.checkpw(password.encode(), objetivo)
    return ok and hash_guardado is not None
