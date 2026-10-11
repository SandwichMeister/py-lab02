from datetime import UTC, datetime

from streamstats.analysis import Stats, analyze
from streamstats.models import Event


def make_event(level="INFO", source="auth", minute=0):
    return Event(datetime(2026, 10, 1, 9, minute, tzinfo=UTC), level, source, "текст")


def test_counts():
    stats = Stats()
    stats.add(make_event("INFO", "auth", minute=5))
    stats.add(make_event("ERROR", "db", minute=1))
    stats.add(make_event("ERROR", "auth", minute=9))
    stats.add(None)

    assert stats.total == 3
    assert stats.skipped == 1
    assert stats.by_level == {"INFO": 1, "ERROR": 2}
    assert stats.by_source == {"auth": 2, "db": 1}
    assert stats.first.minute == 1
    assert stats.last.minute == 9


def test_top_sources():
    stats = Stats()
    for source in ["web", "api", "db", "db", "cache"]:
        stats.add(make_event("ERROR", source))
    stats.add(make_event("CRITICAL", "db"))
    stats.add(make_event("WARNING", "auth"))

    assert stats.top_error_sources() == [("db", 3), ("api", 1), ("cache", 1), ("web", 1)]
    assert stats.top_error_sources(2) == [("db", 3), ("api", 1)]


def test_several_files(tmp_path):
    header = "timestamp,level,source,message\n"
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text(header + "2026-10-01T09:00:00,INFO,auth,один\n", encoding="utf-8")
    second.write_text(
        header + "2026-10-02T09:00:00,ERROR,db,два\n2026-10-03T09:00:00,INFO,auth,три\n",
        encoding="utf-8",
    )

    stats = analyze([str(first), str(second)], "csv")

    assert stats.total == 3
    assert stats.by_source == {"auth": 2, "db": 1}
    assert stats.first.day == 1
    assert stats.last.day == 3
