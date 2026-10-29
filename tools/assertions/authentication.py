import allure
from loguru import logger

from clients.authentication.authentication_schema import LoginResponseSchema
from clients.error_schema import InternalErrorResponseSchema
from tools.assertions.base import assert_equal, assert_is_true
from tools.assertions.errors import assert_internal_error_response
from tools.error_messages import ApiErrorMessage


@allure.step("Check login response")
def assert_login_response(response: LoginResponseSchema) -> None:
    """Проверяет токены в ответе при успешной аутентификации.

    Args:
        response: Ответ API с токенами авторизации.

    Raises:
        AssertionError: Если тип токена отличается от bearer
            или access token либо refresh token пустой.
    """
    logger.info("🔎 Check login response")
    assert_equal(response.token.token_type, "bearer", "token type")
    assert_is_true(response.token.access_token, "access token")
    assert_is_true(response.token.refresh_token, "refresh token")


@allure.step("Check refresh response")
def assert_refresh_response(response: LoginResponseSchema, original_refresh_token: str) -> None:
    """Проверяет токены после refresh и сохранность исходного refresh-токена.

    Args:
        response: Ответ API на обновление токена.
        original_refresh_token: Токен из исходного login-ответа.

    Raises:
        AssertionError: Если токены некорректны или refresh-токен изменился.
    """
    logger.info("🔎 Check refresh response")
    assert_login_response(response=response)
    assert_is_true(
        actual=response.token.refresh_token == original_refresh_token,
        name="refresh token unchanged",
    )


@allure.step("Check invalid refresh token response")
def assert_invalid_refresh_token_response(actual: InternalErrorResponseSchema) -> None:
    """Проверяет причину отказа в обновлении невалидного refresh-токена.

    Args:
        actual: Фактический ответ API с сообщением об ошибке.

    Raises:
        AssertionError: Если сообщение не соответствует невалидному refresh-токену.
    """
    logger.info("🔎 Check invalid refresh token response")
    expected = InternalErrorResponseSchema(detail=ApiErrorMessage.INVALID_OR_EXPIRED_REFRESH_TOKEN)
    assert_internal_error_response(actual=actual, expected=expected)


@allure.step("Check invalid credentials response")
def assert_invalid_credentials_response(actual: InternalErrorResponseSchema) -> None:
    """Проверяет причину отказа во входе с неверными учетными данными.

    Args:
        actual: Фактический ответ API с сообщением об ошибке.

    Raises:
        AssertionError: Если сообщение не соответствует неверным учетным данным.
    """
    logger.info("🔎 Check invalid credentials response")
    expected = InternalErrorResponseSchema(detail=ApiErrorMessage.INVALID_CREDENTIALS)
    assert_internal_error_response(actual=actual, expected=expected)
