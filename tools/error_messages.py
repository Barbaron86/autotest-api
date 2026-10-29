"""Ожидаемые сообщения об ошибках тестируемого API."""

from enum import StrEnum


class ApiErrorMessage(StrEnum):
    """Статичные бизнес-причины ошибок без отдельного машинного кода."""

    USER_NOT_FOUND = "User not found"
    INVALID_SCORE_RANGE = "Value error, max score should not be less than min score"
    INVALID_OR_EXPIRED_REFRESH_TOKEN = "Invalid or expired refresh token"
    INVALID_CREDENTIALS = "Invalid credentials"


class ApiErrorPattern(StrEnum):
    """Статичные шаблоны бизнес-причин с переменными данными ответа."""

    USER_ALREADY_EXISTS = r"User with email (?P<email>.+) already exists"
