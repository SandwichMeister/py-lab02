import argparse
import logging
import os
import sys

from streamstats.analysis import analyze
from streamstats.errors import CliConfigError, StreamStatsError
from streamstats.report import build_report, report_to_json, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="streamstats", description="Потоковый анализатор событий из CSV и JSONL."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    analyze_command = commands.add_parser("analyze", help="посчитать статистику по файлам")
    analyze_command.add_argument("inputs", nargs="+", metavar="INPUT", help="входные файлы")
    analyze_command.add_argument(
        "--format", required=True, choices=("csv", "jsonl"), help="формат входных файлов"
    )
    analyze_command.add_argument(
        "--output", metavar="REPORT.json", help="файл отчета, без него отчет печатается на экран"
    )
    analyze_command.add_argument(
        "--skip-invalid", action="store_true", help="пропускать ошибочные строки"
    )
    return parser


def check_output(inputs: list[str], output: str | None) -> None:
    """Проверяет на совпадение входного и выходного файла."""
    if output is not None:
        for path in inputs:
            if os.path.abspath(path) == os.path.abspath(output):
                raise CliConfigError(f"файл отчета совпадает с входным файлом: {output}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    try:
        check_output(args.inputs, args.output)
        stats = analyze(args.inputs, args.format, args.skip_invalid)
        report = build_report(stats)
        if args.output is None:
            print(report_to_json(report))
        else:
            write_report(report, args.output)
    except StreamStatsError as exc:
        print(f"ошибка: {exc}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as exc:
        print(f"ошибка чтения или записи файла: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
