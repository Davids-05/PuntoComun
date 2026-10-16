from datetime import datetime, timezone


def ahora() -> datetime:
    """Hora actual en UTC sin zona (SQLite guarda fechas sin zona)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
