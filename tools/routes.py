"""Базовые маршруты тестируемого API."""

from enum import StrEnum


class APIRoutes(StrEnum):
    """Маршруты ресурсов API для построения запросов клиентов."""

    USERS = "/api/v1/users"
    FILES = "/api/v1/files"
    COURSES = "/api/v1/courses"
    EXERCISES = "/api/v1/exercises"
    AUTHENTICATION = "/api/v1/authentication"
