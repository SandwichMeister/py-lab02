import logging

import pytest

from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.parsers import read_csv, read_jsonl

CSV_TEXT = """timestamp,level,source,message
2026-10-01T09:00:00,INFO,auth,Пользователь вошёл
2026-10-01T09:00:05,ERROR,db,"Таймаут, повтор"
"""

JSONL_TEXT = """{"timestamp": "2026-10-01T09:00:00", "level": "INFO", "source": "auth", "message": "Пользователь вошёл"}
{"timestamp": "2026-10-01T09:00:05", "level": "ERROR", "source": "db", "message": "Таймаут, повтор"}
"""  # noqa: E501


def write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_read_csv(tmp_path):
    events = list(read_csv(write(tmp_path, "events.csv", CSV_TEXT)))

    assert [event.source for event in events] == ["auth", "db"]
    assert events[0].message == "Пользователь вошёл"
    assert events[1].message == "Таймаут, повтор"


def test_csv_equals_jsonl(tmp_path):
    from_csv = list(read_csv(write(tmp_path, "events.csv", CSV_TEXT)))
    from_jsonl = list(read_jsonl(write(tmp_path, "events.jsonl", JSONL_TEXT)))

    assert from_csv == from_jsonl


def test_empty_files(tmp_path):
    assert list(read_csv(write(tmp_path, "empty.csv", ""))) == []
    assert list(read_jsonl(write(tmp_path, "empty.jsonl", ""))) == []


def test_bad_json(tmp_path):
    good_line = JSONL_TEXT.splitlines()[0]
    path = write(tmp_path, "events.jsonl", "\n".join([good_line] * 6 + ["{не json"]))

    with pytest.raises(InvalidEventError, match="events.jsonl, строка 7: неверный JSON"):
        list(read_jsonl(path))


def test_bad_timestamp(tmp_path):
    path = write(tmp_path, "events.csv", CSV_TEXT + "вчера,INFO,api,Привет\n")

    with pytest.raises(InvalidTimestampError, match="events.csv, строка 4: .*timestamp"):
        list(read_csv(path))


def test_skip_invalid(tmp_path, caplog):
    text = CSV_TEXT + "вчера,INFO,api,Привет\n2026-10-01T09:05:00,INFO,api,Готово\n"
    path = write(tmp_path, "events.csv", text)

    with caplog.at_level(logging.WARNING):
        events = list(read_csv(path, skip_invalid=True))

    assert events[2] is None
    assert [event.source for event in events if event is not None] == ["auth", "db", "api"]
    assert "строка 4" in caplog.text
