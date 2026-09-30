from clients.authentication.authentication_schema import LoginResponseSchema
from tools.assertions.base import assert_equal, assert_is_true


def assert_login_response(response: LoginResponseSchema) -> None:
    """Проверяет токены в ответе при успешной аутентификации.

    Args:
        response: Ответ API с токенами авторизации.

    Raises:
        AssertionError: Если тип токена отличается от bearer
            или access token либо refresh token пустой.
    """
    assert_equal(response.token.token_type, "bearer", "token type")
    assert_is_true(response.token.access_token, "access token")
    assert_is_true(response.token.refresh_token, "refresh token")
