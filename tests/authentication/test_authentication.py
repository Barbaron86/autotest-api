from http import HTTPStatus

import allure
import pytest
from allure_commons.types import Severity

from clients.authentication.authentication_client import AuthenticationClient
from clients.authentication.authentication_schema import LoginRequestSchema, LoginResponseSchema, RefreshRequestSchema
from clients.error_schema import InternalErrorResponseSchema
from fixtures.users import UserFixture
from tools.allure.epics import AllureEpic
from tools.allure.features import AllureFeature
from tools.allure.stories import AllureStory
from tools.allure.tags import AllureTag
from tools.assertions.authentication import (
    assert_invalid_credentials_response,
    assert_invalid_refresh_token_response,
    assert_login_response,
    assert_refresh_response,
)
from tools.assertions.base import assert_status_code
from tools.assertions.schema import validate_json_schema
from tools.fakers import fake


@pytest.mark.regression
@pytest.mark.authentication
@allure.tag(AllureTag.AUTHENTICATION, AllureTag.REGRESSION)
@allure.epic(AllureEpic.LMS)
@allure.feature(AllureFeature.AUTHENTICATION)
@allure.parent_suite(AllureEpic.LMS)
@allure.suite(AllureFeature.AUTHENTICATION)
class TestAuthentication:
    @allure.story(AllureStory.LOGIN)
    @allure.sub_suite(AllureStory.LOGIN)
    @allure.title("Login with correct email and password")
    @allure.severity(Severity.BLOCKER)
    def test_login(self, function_user: UserFixture, authentication_client: AuthenticationClient) -> None:
        """Проверяет успешную аутентификацию пользователя.

        Выполняет вход с учетными данными из фикстуры и проверяет
        HTTP-статус, токены и JSON Schema ответа.

        Args:
            function_user: Фикстура с данными созданного пользователя.
            authentication_client: Фикстура API-клиента аутентификации.

        Raises:
            AssertionError: Если HTTP-статус или токены не соответствуют ожиданиям.
        """
        login_request = LoginRequestSchema(email=function_user.email, password=function_user.password)
        login_response = authentication_client.login_api(request=login_request)

        assert_status_code(actual=login_response.status_code, expected=HTTPStatus.OK)
        login_response_data = LoginResponseSchema.model_validate_json(login_response.text)
        assert_login_response(response=login_response_data)

        validate_json_schema(instance=login_response.json(), schema=LoginResponseSchema.model_json_schema())

    @allure.story(AllureStory.REFRESH_TOKEN)
    @allure.sub_suite(AllureStory.REFRESH_TOKEN)
    @allure.title("Refresh access token")
    @allure.severity(Severity.CRITICAL)
    def test_refresh_token(self, function_user: UserFixture, authentication_client: AuthenticationClient) -> None:
        """Проверяет успешное обновление access-токена.

        Авторизует пользователя, получает refresh-токен и использует его
        для запроса нового access-токена. Проверяет HTTP-статус,
        структуру ответа, наличие токенов и сохранность refresh-токена.

        Args:
            function_user: Фикстура с данными созданного пользователя.
            authentication_client: Фикстура API-клиента аутентификации.

        Raises:
            AssertionError: Если HTTP-статус или данные токенов
                не соответствуют ожидаемым значениям.
        """
        login_request = LoginRequestSchema(email=function_user.email, password=function_user.password)
        login_response = authentication_client.login_api(request=login_request)

        assert_status_code(actual=login_response.status_code, expected=HTTPStatus.OK)

        login_response_data = LoginResponseSchema.model_validate_json(login_response.text)
        assert_login_response(response=login_response_data)

        original_refresh_token = login_response_data.token.refresh_token
        refresh_request = RefreshRequestSchema(refresh_token=original_refresh_token)

        refresh_response = authentication_client.refresh_api(request=refresh_request)

        assert_status_code(actual=refresh_response.status_code, expected=HTTPStatus.OK)

        refresh_response_data = LoginResponseSchema.model_validate_json(refresh_response.text)
        validate_json_schema(instance=refresh_response.json(), schema=LoginResponseSchema.model_json_schema())

        assert_refresh_response(response=refresh_response_data, original_refresh_token=original_refresh_token)

    @allure.tag(AllureTag.VALIDATE_ENTITY)
    @allure.story(AllureStory.LOGIN)
    @allure.sub_suite(AllureStory.LOGIN)
    @allure.title("Login with incorrect password")
    @allure.severity(Severity.CRITICAL)
    def test_login_with_incorrect_password(
        self,
        function_user_with_verified_credentials: UserFixture,
        authentication_client: AuthenticationClient,
    ) -> None:
        """Проверяет запрет входа с неверным паролем существующего пользователя.

        Использует пользователя с проверенным входом по правильному паролю.
        Передает правильный email и гарантированно другой пароль,
        проверяет HTTP-статус, точное сообщение и JSON Schema ошибки.

        Args:
            function_user_with_verified_credentials: Фикстура пользователя
                с проверенными учетными данными для входа.
            authentication_client: Фикстура API-клиента аутентификации.

        Raises:
            AssertionError: Если HTTP-статус, сообщение или структура
                ошибки не соответствуют ожиданиям.
        """
        incorrect_password = fake.password_different_from(function_user_with_verified_credentials.password)
        login_request = LoginRequestSchema(
            email=function_user_with_verified_credentials.email,
            password=incorrect_password,
        )
        login_response = authentication_client.login_api(request=login_request)

        assert_status_code(actual=login_response.status_code, expected=HTTPStatus.UNAUTHORIZED)
        validate_json_schema(instance=login_response.json(), schema=InternalErrorResponseSchema.model_json_schema())

        login_response_data = InternalErrorResponseSchema.model_validate_json(login_response.text)
        assert_invalid_credentials_response(actual=login_response_data)

    @allure.tag(AllureTag.VALIDATE_ENTITY)
    @allure.story(AllureStory.REFRESH_TOKEN)
    @allure.sub_suite(AllureStory.REFRESH_TOKEN)
    @allure.title("Refresh with invalid token")
    @allure.severity(Severity.CRITICAL)
    def test_refresh_with_invalid_token(self, authentication_client: AuthenticationClient) -> None:
        """Проверяет запрет обновления access-токена с невалидным refresh-токеном.

        Передает сгенерированный UUID вместо JWT и проверяет HTTP-статус,
        точное сообщение и JSON Schema ошибки.

        Args:
            authentication_client: Фикстура API-клиента аутентификации.

        Raises:
            AssertionError: Если HTTP-статус, сообщение или структура
                ошибки не соответствуют ожиданиям.
        """
        invalid_refresh_token = fake.uuid4()
        refresh_request = RefreshRequestSchema(refresh_token=invalid_refresh_token)
        refresh_response = authentication_client.refresh_api(request=refresh_request)

        assert_status_code(actual=refresh_response.status_code, expected=HTTPStatus.UNAUTHORIZED)
        refresh_response_data = InternalErrorResponseSchema.model_validate_json(refresh_response.text)
        assert_invalid_refresh_token_response(actual=refresh_response_data)
        validate_json_schema(instance=refresh_response.json(), schema=InternalErrorResponseSchema.model_json_schema())
