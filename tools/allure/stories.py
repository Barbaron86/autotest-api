from enum import StrEnum


class AllureStory(StrEnum):
    """Сценарии для группировки тестов в Allure."""

    LOGIN = "Login"
    GET_ENTITY = "Get entity"
    GET_ENTITIES = "Get entities"
    CREATE_ENTITY = "Create entity"
    UPDATE_ENTITY = "Update entity"
    DELETE_ENTITY = "Delete entity"
    VALIDATE_ENTITY = "Validate entity"
