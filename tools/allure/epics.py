from enum import StrEnum


class AllureEpic(StrEnum):
    """Основные сервисы системы в иерархии Allure."""

    LMS = "LMS service"
    STUDENT = "Student service"
    ADMINISTRATION = "Administration service"
