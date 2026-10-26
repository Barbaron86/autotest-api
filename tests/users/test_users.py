from http import HTTPStatus

import allure
import pytest
from allure_commons.types import Severity

from clients.users.private_users_client import PrivateUsersClient
from clients.users.public_users_client import PublicUsersClient
from clients.users.user_schema import (
    CreateUserRequestSchema,
    CreateUserResponseSchema,
    GetUserResponseSchema,
    UpdateUserRequestSchema,
    UpdateUserResponseSchema,
)
from fixtures.users import UserFixture
from tools.allure.epics import AllureEpic
from tools.allure.features import AllureFeature
from tools.allure.stories import AllureStory
from tools.allure.tags import AllureTag
from tools.assertions.base import assert_status_code
from tools.assertions.schema import validate_json_schema
from tools.assertions.users import (
    assert_create_user_response,
    assert_get_user_response,
    assert_update_user_response,
    assert_user,
)
from tools.fakers import fake


@pytest.mark.users
@pytest.mark.regression
@allure.tag(AllureTag.USERS, AllureTag.REGRESSION)
@allure.epic(AllureEpic.LMS)
@allure.feature(AllureFeature.USERS)
@allure.parent_suite(AllureEpic.LMS)
@allure.suite(AllureFeature.USERS)
class TestUsers:
    @pytest.mark.parametrize("email", ["mail.ru", "gmail.com", "example.com"])
    @allure.tag(AllureTag.CREATE_ENTITY)
    @allure.story(AllureStory.CREATE_ENTITY)
    @allure.sub_suite(AllureStory.CREATE_ENTITY)
    @allure.title("Create user with email domain {email}")
    @allure.severity(Severity.BLOCKER)
    def test_create_user(self, email: str, public_users_client: PublicUsersClient) -> None:
        """Проверяет создание пользователя с email на заданном домене.

        Создает пользователя со сгенерированными данными и проверяет
        HTTP-статус, данные пользователя и JSON Schema ответа.

        Args:
            email: Домен для генерации случайного email-адреса.
            public_users_client: Фикстура публичного API-клиента пользователей.

        Raises:
            AssertionError: Если HTTP-статус или данные пользователя
                не соответствуют ожиданиям.
        """
        request = CreateUserRequestSchema(email=fake.email(domain=email))
        response = public_users_client.create_user_api(request=request)

        assert_status_code(actual=response.status_code, expected=HTTPStatus.OK)
        response_data = CreateUserResponseSchema.model_validate_json(response.text)
        assert_create_user_response(request=request, response=response_data)

        validate_json_schema(response.json(), response_data.model_json_schema())

    @allure.tag(AllureTag.GET_ENTITY)
    @allure.story(AllureStory.GET_ENTITY)
    @allure.sub_suite(AllureStory.GET_ENTITY)
    @allure.title("Get user me")
    @allure.severity(Severity.CRITICAL)
    def test_get_user_me(self, private_users_client: PrivateUsersClient, function_user: UserFixture) -> None:
        """Проверяет получение данных текущего пользователя.

        Запрашивает данные авторизованного пользователя и проверяет
        HTTP-статус, совпадение данных с ответом на создание и JSON Schema.

        Args:
            private_users_client: Фикстура авторизованного API-клиента пользователей.
            function_user: Фикстура с данными созданного пользователя.

        Raises:
            AssertionError: Если HTTP-статус или данные пользователя
                не соответствуют ожиданиям.
        """
        response = private_users_client.get_user_me_api()

        assert_status_code(actual=response.status_code, expected=HTTPStatus.OK)
        response_data = GetUserResponseSchema.model_validate_json(response.text)
        assert_get_user_response(get_user_response=response_data, create_user_response=function_user.response)

        validate_json_schema(instance=response.json(), schema=GetUserResponseSchema.model_json_schema())

    @allure.tag(AllureTag.GET_ENTITY)
    @allure.story(AllureStory.GET_ENTITY)
    @allure.sub_suite(AllureStory.GET_ENTITY)
    @allure.title("Get user me by {user_id}")
    @allure.severity(Severity.NORMAL)
    def test_get_user_by_id(self, private_users_client: PrivateUsersClient, function_user: UserFixture) -> None:
        """Проверяет получение данных пользователя по идентификатору.

        Запрашивает данные пользователя по его идентификатору и проверяет
        HTTP-статус, совпадение данных с ответом на создание и JSON Schema.

        Args:
            private_users_client: Фикстура авторизованного API-клиента пользователей.
            function_user: Фикстура с данными созданного пользователя.
        """

        response = private_users_client.get_user_api(user_id=function_user.response.user.id)

        assert_status_code(actual=response.status_code, expected=HTTPStatus.OK)

        response_data = GetUserResponseSchema.model_validate_json(response.text)
        assert_get_user_response(get_user_response=response_data, create_user_response=function_user.response)

        validate_json_schema(instance=response.json(), schema=GetUserResponseSchema.model_json_schema())

    @allure.tag(AllureTag.UPDATE_ENTITY)
    @allure.story(AllureStory.UPDATE_ENTITY)
    @allure.sub_suite(AllureStory.UPDATE_ENTITY)
    @allure.title("Partial update user")
    @allure.severity(Severity.CRITICAL)
    def test_partial_update_user(self, private_users_client: PrivateUsersClient, function_user: UserFixture) -> None:
        """Проверяет частичное обновление данных пользователя.

        Изменяет имя пользователя через PATCH и проверяет HTTP-статус,
        JSON Schema, корректность обновления и сохранность остальных полей.
        Повторно запрашивает пользователя через GET и проверяет,
        что обновленные данные сохранились на сервере.

        Args:
            private_users_client: Фикстура авторизованного API-клиента пользователей.
            function_user: Фикстура с исходными данными созданного пользователя.

        Raises:
            AssertionError: Если HTTP-статус, структура ответа или данные
                пользователя не соответствуют ожидаемым значениям.
        """
        original_user = function_user.response.user
        request = UpdateUserRequestSchema(first_name="Александр")

        update_response = private_users_client.update_user_api(user_id=original_user.id, request=request)

        assert_status_code(actual=update_response.status_code, expected=HTTPStatus.OK)

        update_response_data = UpdateUserResponseSchema.model_validate_json(update_response.text)
        validate_json_schema(instance=update_response.json(), schema=UpdateUserResponseSchema.model_json_schema())

        assert_update_user_response(request=request, response=update_response_data, original_user=original_user)

        get_response = private_users_client.get_user_api(user_id=original_user.id)

        assert_status_code(actual=get_response.status_code, expected=HTTPStatus.OK)

        get_response_data = GetUserResponseSchema.model_validate_json(get_response.text)
        validate_json_schema(instance=get_response.json(), schema=GetUserResponseSchema.model_json_schema())

        assert_user(actual=get_response_data.user, expected=update_response_data.user)
