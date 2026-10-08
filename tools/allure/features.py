from enum import StrEnum


class AllureFeature(StrEnum):
    """Функциональные области API в Allure-отчете."""

    USERS = "Users"
    FILES = "Files"
    COURSES = "Courses"
    EXERCISES = "Exercises"
    AUTHENTICATION = "Authentication"
