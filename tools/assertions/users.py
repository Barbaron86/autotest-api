from clients.users.user_schema import CreateUserRequestSchema, CreateUserResponseSchema
from tools.assertions.base import assert_equal


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
    assert_equal(response.user.email, request.email, "Email")
    assert_equal(response.user.first_name, request.first_name, "First name")
    assert_equal(response.user.last_name, request.last_name, "Last name")
    assert_equal(response.user.middle_name, request.middle_name, "Middle name")
