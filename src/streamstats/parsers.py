"""парсеры CSV и JSONL."""

import csv
import json
import logging
from collections.abc import Iterator

from streamstats.errors import InvalidEventError, UnsupportedFormatError
from streamstats.models import Event, make_event

logger = logging.getLogger(__name__)


def handle_bad_line(exc: InvalidEventError, path: str, line: int, skip_invalid: bool) -> None:
    """Остановить обработку либо записать WARNING и идти дальше."""
    message = f"{path}, строка {line}: {exc}"
    if not skip_invalid:
        raise type(exc)(message) from exc
    logger.warning("строка пропущена: %s", message)


def parse_json_line(line: str) -> dict:
    """Превратить одну строку JSONL в словарь полей."""
    try:
        raw = json.loads(line)
    except json.JSONDecodeError as exc:
        raise InvalidEventError(f"неверный JSON: {exc.msg}") from exc
    if not isinstance(raw, dict):
        raise InvalidEventError("строка JSONL должна быть объектом")
    return raw


def read_csv(path: str, skip_invalid: bool = False) -> Iterator[Event | None]:
    """Читать события из CSV по одному."""
    with open(path, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                event = make_event(row)
            except InvalidEventError as exc:
                handle_bad_line(exc, path, reader.line_num, skip_invalid)
                event = None
            yield event


def read_jsonl(path: str, skip_invalid: bool = False) -> Iterator[Event | None]:
    """Читать события из JSONL по одному."""
    with open(path, encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            if line.strip() == "":
                continue
            try:
                event = make_event(parse_json_line(line))
            except InvalidEventError as exc:
                handle_bad_line(exc, path, line_number, skip_invalid)
                event = None
            yield event


def read_events(path: str, fmt: str, skip_invalid: bool = False) -> Iterator[Event | None]:
    """Выбрать парсер."""
    if fmt == "csv":
        return read_csv(path, skip_invalid)
    if fmt == "jsonl":
        return read_jsonl(path, skip_invalid)
    raise UnsupportedFormatError(f"неподдерживаемый формат: '{fmt}'")
