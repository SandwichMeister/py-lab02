"""Анализ статистики."""

from collections import Counter
from datetime import datetime

from streamstats.models import ERROR_LEVELS, Event
from streamstats.parsers import read_events


class Stats:
    """Счётчики по всем прочитанным событиям"""

    def __init__(self) -> None:
        self.total = 0
        self.skipped = 0
        self.by_level: Counter[str] = Counter()
        self.by_source: Counter[str] = Counter()
        self.error_sources: Counter[str] = Counter()
        self.first: datetime | None = None
        self.last: datetime | None = None

    def add(self, event: Event | None) -> None:
        """Учесть одно событие; None означает пропущенную строку."""
        if event is None:
            self.skipped += 1
            return

        self.total += 1
        self.by_level[event.level] += 1
        self.by_source[event.source] += 1
        if event.level in ERROR_LEVELS:
            self.error_sources[event.source] += 1

        if self.first is None or event.timestamp < self.first:
            self.first = event.timestamp
        if self.last is None or event.timestamp > self.last:
            self.last = event.timestamp

    def top_error_sources(self, n: int = 5) -> list[tuple[str, int]]:
        """Вернуть n источников с наибольшим числом ошибок; при равенстве — по алфавиту."""
        pairs = sorted(self.error_sources.items(), key=lambda pair: (-pair[1], pair[0]))
        return pairs[:n]


def analyze(paths: list[str], fmt: str, skip_invalid: bool = False) -> Stats:
    """Прочитать все файлы по очереди и собрать общую статистику."""
    stats = Stats()
    for path in paths:
        for event in read_events(path, fmt, skip_invalid):
            stats.add(event)
    return stats
