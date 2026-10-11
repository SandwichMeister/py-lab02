"""Модель события и валидация обязательных полей."""

from dataclasses import dataclass
from datetime import UTC, datetime

from streamstats.errors import InvalidEventError, InvalidTimestampError

FIELDS = ("timestamp", "level", "source", "message")
LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
ERROR_LEVELS = ("ERROR", "CRITICAL")


@dataclass
class Event:
    """Одно событие из входного файла."""

    timestamp: datetime
    level: str
    source: str
    message: str


def make_event(raw: dict) -> Event:
    """Проверить поля и собрать из них событие."""
    for field in FIELDS:
        if not isinstance(raw.get(field), str):
            raise InvalidEventError(f"поле '{field}' отсутствует")

    if raw["level"] not in LEVELS:
        raise InvalidEventError(f"неизвестный уровень в поле 'level': '{raw['level']}'")

    if raw["source"].strip() == "":
        raise InvalidEventError("поле 'source' не должно быть пустым")

    try:
        timestamp = datetime.fromisoformat(raw["timestamp"])
    except ValueError as exc:
        raise InvalidTimestampError(
            f"неверная временная метка в поле 'timestamp': '{raw['timestamp']}'"
        ) from exc
    # метку без часового пояса считаем в UTC
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)

    return Event(timestamp, raw["level"], raw["source"], raw["message"])
