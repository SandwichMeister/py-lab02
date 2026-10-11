import json

from streamstats.__main__ import main

CSV_TEXT = """timestamp,level,source,message
2026-10-01T09:00:00,INFO,auth,Пользователь вошёл
2026-10-01T09:00:05,ERROR,платежи,Таймаут соединения
2026-10-01T09:02:00,CRITICAL,платежи,Диск переполнен
"""


def write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def read_report(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def test_full_report(tmp_path):
    source = write(tmp_path, "events.csv", CSV_TEXT)
    output = str(tmp_path / "report.json")

    code = main(["analyze", source, "--format", "csv", "--output", output])

    assert code == 0
    assert read_report(output) == {
        "total_events": 3,
        "skipped_lines": 0,
        "by_level": {"DEBUG": 0, "INFO": 1, "WARNING": 0, "ERROR": 1, "CRITICAL": 1},
        "by_source": {"auth": 1, "платежи": 2},
        "top_error_sources": [{"source": "платежи", "count": 2}],
        "first_timestamp": "2026-10-01T09:00:00+00:00",
        "last_timestamp": "2026-10-01T09:02:00+00:00",
    }
    with open(source, encoding="utf-8") as file:
        assert file.read() == CSV_TEXT


def test_empty_file(tmp_path):
    source = write(tmp_path, "empty.jsonl", "")
    output = str(tmp_path / "report.json")

    code = main(["analyze", source, "--format", "jsonl", "--output", output])

    report = read_report(output)
    assert code == 0
    assert report["total_events"] == 0
    assert report["first_timestamp"] is None


def test_bad_line(tmp_path, capsys):
    source = write(tmp_path, "events.csv", CSV_TEXT + "вчера,INFO,api,Привет\n")
    output = tmp_path / "report.json"

    code = main(["analyze", source, "--format", "csv", "--output", str(output)])

    assert code == 2
    assert "events.csv, строка 5" in capsys.readouterr().err
    assert not output.exists()


def test_skip_invalid(tmp_path):
    source = write(tmp_path, "events.csv", CSV_TEXT + "вчера,INFO,api,Привет\n")
    output = str(tmp_path / "report.json")

    code = main(["analyze", source, "--format", "csv", "--output", output, "--skip-invalid"])

    report = read_report(output)
    assert code == 0
    assert report["total_events"] == 3
    assert report["skipped_lines"] == 1
