from http import HTTPStatus

import allure
import pytest
from allure_commons.types import Severity

from clients.authentication.authentication_client import AuthenticationClient
from clients.authentication.authentication_schema import LoginRequestSchema, LoginResponseSchema
from fixtures.users import UserFixture
from tools.allure.epics import AllureEpic
from tools.allure.features import AllureFeature
from tools.allure.stories import AllureStory
from tools.allure.tags import AllureTag
from tools.assertions.authentication import assert_login_response
from tools.assertions.base import assert_status_code
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
