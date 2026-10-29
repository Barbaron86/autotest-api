"""Машинные типы ошибок валидации тестируемого API."""

from enum import StrEnum


class ValidationErrorType(StrEnum):
    """Типы ошибок, используемые в ожиданиях API-тестов."""

    STRING_TOO_LONG = "string_too_long"
    STRING_TOO_SHORT = "string_too_short"
    UUID_PARSING = "uuid_parsing"
    VALUE_ERROR = "value_error"
