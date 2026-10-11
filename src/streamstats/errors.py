"""Исключения пакета"""

class StreamStatsError(Exception):
    """Базовая ошибка пакета"""


class UnsupportedFormatError(StreamStatsError):
    """Некорректный формат"""


class InvalidEventError(StreamStatsError):
    """Строка входного - некорректное событие"""


class InvalidTimestampError(InvalidEventError):
    """Timestamp не разбирается как ISO 8601"""


class CliConfigError(StreamStatsError):
    """Аргументы командной строки заданы неверно"""
