import allure

from clients.users.user_schema import (
    CreateUserRequestSchema,
    CreateUserResponseSchema,
    GetUserResponseSchema,
    UserSchema,
)
from tools.assertions.base import assert_equal
from tools.logger import get_logger

logger = get_logger("USERS_ASSERTIONS")


@allure.step("Check create user response")
def assert_create_user_response(request: CreateUserRequestSchema, response: CreateUserResponseSchema) -> None:
    """Проверяет данные созданного пользователя в ответе API.

    Сравнивает данные пользователя из ответа API
    с данными, переданными в запросе на создание пользователя.

    Args:
        request: Данные запроса на создание пользователя.
        response: Ответ API с данными созданного пользователя.

    Raises:
        AssertionError: Если данные пользователя в ответе
            не совпадают с данными запроса.
    """
    logger.info("Check create user response")
    assert_equal(response.user.email, request.email, "Email")
    assert_equal(response.user.first_name, request.first_name, "First name")
    assert_equal(response.user.last_name, request.last_name, "Last name")
    assert_equal(response.user.middle_name, request.middle_name, "Middle name")


@allure.step("Check user")
def assert_user(actual: UserSchema, expected: UserSchema) -> None:
    """Проверяет совпадение данных пользователя.

    Сравнивает идентификатор, email, фамилию, имя и отчество.

    Args:
        actual: Фактические данные пользователя.
        expected: Ожидаемые данные пользователя.

    Raises:
        AssertionError: Если хотя бы одно поле пользователя не совпадает.
    """
    logger.info("Check user")
    assert_equal(actual.id, expected.id, "ID")
    assert_equal(actual.email, expected.email, "Email")
    assert_equal(actual.last_name, expected.last_name, "Last name")
    assert_equal(actual.first_name, expected.first_name, "First name")
    assert_equal(actual.middle_name, expected.middle_name, "Middle name")


@allure.step("Check get user response")
def assert_get_user_response(
    get_user_response: GetUserResponseSchema,
    create_user_response: CreateUserResponseSchema,
) -> None:
    """Проверяет данные пользователя в ответе на запрос получения.

    Сравнивает полученного пользователя с данными ответа на создание.

    Args:
        get_user_response: Ответ API на запрос получения пользователя.
        create_user_response: Ответ API на запрос создания пользователя.

    Raises:
        AssertionError: Если данные полученного пользователя
            не совпадают с данными созданного пользователя.
    """
    logger.info("Check get user response")
    assert_user(actual=get_user_response.user, expected=create_user_response.user)
