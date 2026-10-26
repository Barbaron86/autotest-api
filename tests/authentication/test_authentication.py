from http import HTTPStatus

import allure
import pytest
from allure_commons.types import Severity

from clients.authentication.authentication_client import AuthenticationClient
from clients.authentication.authentication_schema import LoginRequestSchema, LoginResponseSchema, RefreshRequestSchema
from fixtures.users import UserFixture
from tools.allure.epics import AllureEpic
from tools.allure.features import AllureFeature
from tools.allure.stories import AllureStory
from tools.allure.tags import AllureTag
from tools.assertions.authentication import assert_login_response
from tools.assertions.base import assert_is_true, assert_status_code
from tools.assertions.schema import validate_json_schema


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
        request = LoginRequestSchema(email=function_user.email, password=function_user.password)
        response = authentication_client.login_api(request=request)

        assert_status_code(actual=response.status_code, expected=HTTPStatus.OK)
        response_data = LoginResponseSchema.model_validate_json(response.text)
        assert_login_response(response=response_data)

        validate_json_schema(instance=response.json(), schema=LoginResponseSchema.model_json_schema())

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

        assert_login_response(response=refresh_response_data)

        is_same_refresh_token = refresh_response_data.token.refresh_token == original_refresh_token
        assert_is_true(actual=is_same_refresh_token, name="refresh token unchanged")
