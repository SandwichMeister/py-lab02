from datetime import UTC, datetime

import pytest

from streamstats.errors import InvalidEventError
from streamstats.models import Event, make_event


def make_raw():
    return {
        "timestamp": "2026-10-01T09:00:00",
        "level": "INFO",
        "source": "auth",
        "message": "Пользователь вошёл",
    }


def test_valid_event():
    event = make_event(make_raw())

    assert event == Event(
        timestamp=datetime(2026, 10, 1, 9, 0, tzinfo=UTC),
        level="INFO",
        source="auth",
        message="Пользователь вошёл",
    )


def test_bad_fields():
    bad_values = {"timestamp": "вчера", "level": "NOTICE", "source": "   ", "message": None}

    for field, value in bad_values.items():
        raw = make_raw()
        raw[field] = value

        with pytest.raises(InvalidEventError, match=field):
            make_event(raw)
