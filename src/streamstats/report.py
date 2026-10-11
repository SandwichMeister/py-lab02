"""Формирование JSON-отчёта."""

import json

from streamstats.analysis import Stats
from streamstats.models import LEVELS


def build_report(stats: Stats, top_n: int = 5) -> dict:
    """Превратить статистику в словарь, готовый к записи в JSON."""
    top = [{"source": source, "count": count} for source, count in stats.top_error_sources(top_n)]
    return {
        "total_events": stats.total,
        "skipped_lines": stats.skipped,
        "by_level": {level: stats.by_level[level] for level in LEVELS},
        "by_source": dict(sorted(stats.by_source.items())),
        "top_error_sources": top,
        "first_timestamp": stats.first.isoformat() if stats.first else None,
        "last_timestamp": stats.last.isoformat() if stats.last else None,
    }


def report_to_json(report: dict) -> str:
    """Превратить отчёт в текст JSON, кириллица остаётся читаемой."""
    return json.dumps(report, ensure_ascii=False, indent=2)


def write_report(report: dict, path: str) -> None:
    """Записать отчёт в файл."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(report_to_json(report) + "\n")
