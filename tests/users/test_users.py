from http import HTTPStatus

import allure
import pytest
from allure_commons.types import Severity

from clients.authentication.authentication_client import AuthenticationClient
from clients.authentication.authentication_schema import LoginRequestSchema, LoginResponseSchema
from clients.error_schema import InternalErrorResponseSchema
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
from tools.assertions.authentication import assert_login_response
from tools.assertions.base import assert_status_code
from tools.assertions.schema import validate_json_schema
from tools.assertions.users import (
    assert_create_user_response,
    assert_get_user_response,
    assert_update_user_response,
    assert_user,
    assert_user_not_found_response,
    assert_user_with_existing_email_response,
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
        create_user_request = CreateUserRequestSchema(email=fake.email(domain=email))
        create_user_response = public_users_client.create_user_api(request=create_user_request)

        assert_status_code(actual=create_user_response.status_code, expected=HTTPStatus.OK)
        create_user_response_data = CreateUserResponseSchema.model_validate_json(create_user_response.text)
        assert_create_user_response(request=create_user_request, response=create_user_response_data)

        validate_json_schema(create_user_response.json(), create_user_response_data.model_json_schema())

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
        get_user_me_response = private_users_client.get_user_me_api()

        assert_status_code(actual=get_user_me_response.status_code, expected=HTTPStatus.OK)
        get_user_me_response_data = GetUserResponseSchema.model_validate_json(get_user_me_response.text)
        assert_get_user_response(
            get_user_response=get_user_me_response_data, create_user_response=function_user.response
        )

        validate_json_schema(instance=get_user_me_response.json(), schema=GetUserResponseSchema.model_json_schema())

    @allure.tag(AllureTag.GET_ENTITY)
    @allure.story(AllureStory.GET_ENTITY)
    @allure.sub_suite(AllureStory.GET_ENTITY)
    @allure.title("Get user by ID")
    @allure.severity(Severity.NORMAL)
    def test_get_user_by_id(self, private_users_client: PrivateUsersClient, function_user: UserFixture) -> None:
        """Проверяет получение данных пользователя по идентификатору.

        Запрашивает данные пользователя по его идентификатору и проверяет
        HTTP-статус, совпадение данных с ответом на создание и JSON Schema.

        Args:
            private_users_client: Фикстура авторизованного API-клиента пользователей.
            function_user: Фикстура с данными созданного пользователя.
        """

        get_user_response = private_users_client.get_user_api(user_id=function_user.response.user.id)

        assert_status_code(actual=get_user_response.status_code, expected=HTTPStatus.OK)

        get_user_response_data = GetUserResponseSchema.model_validate_json(get_user_response.text)
        assert_get_user_response(get_user_response=get_user_response_data, create_user_response=function_user.response)

        validate_json_schema(instance=get_user_response.json(), schema=GetUserResponseSchema.model_json_schema())

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
        new_first_name = fake.first_name()
        while new_first_name == original_user.first_name:
            new_first_name = fake.first_name()

        update_user_request = UpdateUserRequestSchema(first_name=new_first_name)

        update_user_response = private_users_client.update_user_api(
            user_id=original_user.id, request=update_user_request
        )

        assert_status_code(actual=update_user_response.status_code, expected=HTTPStatus.OK)

        update_user_response_data = UpdateUserResponseSchema.model_validate_json(update_user_response.text)
        validate_json_schema(instance=update_user_response.json(), schema=UpdateUserResponseSchema.model_json_schema())

        assert_update_user_response(
            request=update_user_request, response=update_user_response_data, original_user=original_user
        )

        get_user_response = private_users_client.get_user_api(user_id=original_user.id)

        assert_status_code(actual=get_user_response.status_code, expected=HTTPStatus.OK)

        get_user_response_data = GetUserResponseSchema.model_validate_json(get_user_response.text)
        validate_json_schema(instance=get_user_response.json(), schema=GetUserResponseSchema.model_json_schema())

        assert_user(actual=get_user_response_data.user, expected=update_user_response_data.user)

    @allure.tag(AllureTag.DELETE_ENTITY)
    @allure.story(AllureStory.DELETE_ENTITY)
    @allure.sub_suite(AllureStory.DELETE_ENTITY)
    @allure.title("Delete user by ID")
    @allure.severity(Severity.CRITICAL)
    def test_delete_user(
        self,
        private_users_client: PrivateUsersClient,
        function_user: UserFixture,
        function_user_to_delete: UserFixture,
    ) -> None:
        """Проверяет удаление отдельного пользователя по идентификатору.

        Получает из фикстуры отдельного доступного пользователя, удаляет
        и ожидает ошибку при повторном GET. Проверяет сохранность пользователя,
        от имени которого выполнялись запросы.

        Args:
            private_users_client: Фикстура авторизованного API-клиента пользователей.
            function_user: Фикстура пользователя, от имени которого идут запросы.
            function_user_to_delete: Проверенная отдельная цель удаления.

        Raises:
            AssertionError: Если HTTP-статус, данные, структура ответа
                или состояние пользователей не соответствуют ожиданиям.
        """
        user_id = function_user_to_delete.response.user.id
        delete_user_response = private_users_client.delete_user_api(user_id=user_id)

        assert_status_code(actual=delete_user_response.status_code, expected=HTTPStatus.OK)

        get_deleted_user_response = private_users_client.get_user_api(user_id=user_id)

        assert_status_code(actual=get_deleted_user_response.status_code, expected=HTTPStatus.NOT_FOUND)
        get_deleted_user_response_data = InternalErrorResponseSchema.model_validate_json(get_deleted_user_response.text)
        assert_user_not_found_response(actual=get_deleted_user_response_data)
        validate_json_schema(
            instance=get_deleted_user_response.json(), schema=InternalErrorResponseSchema.model_json_schema()
        )

        get_observer_user_response = private_users_client.get_user_api(user_id=function_user.response.user.id)

        assert_status_code(actual=get_observer_user_response.status_code, expected=HTTPStatus.OK)
        get_observer_user_response_data = GetUserResponseSchema.model_validate_json(get_observer_user_response.text)
        assert_user(actual=get_observer_user_response_data.user, expected=function_user.response.user)
        validate_json_schema(
            instance=get_observer_user_response.json(), schema=GetUserResponseSchema.model_json_schema()
        )

    @allure.tag(AllureTag.GET_ENTITY)
    @allure.story(AllureStory.GET_ENTITY)
    @allure.sub_suite(AllureStory.GET_ENTITY)
    @allure.title("Get nonexistent user")
    @allure.severity(Severity.NORMAL)
    def test_get_nonexistent_user(self, private_users_client: PrivateUsersClient) -> None:
        """Проверяет получение пользователя с несуществующим идентификатором.

        Отправляет GET со свежим валидным UUID, для которого не создаёт
        пользователя, и проверяет HTTP-статус,
        точное сообщение об отсутствии пользователя и JSON Schema ошибки.

        Args:
            private_users_client: Фикстура авторизованного API-клиента пользователей.

        Raises:
            AssertionError: Если HTTP-статус, сообщение или структура
                ошибки не соответствуют ожиданиям.
        """
        nonexistent_user_id = fake.uuid4()
        get_user_response = private_users_client.get_user_api(user_id=nonexistent_user_id)

        assert_status_code(actual=get_user_response.status_code, expected=HTTPStatus.NOT_FOUND)
        get_user_response_data = InternalErrorResponseSchema.model_validate_json(get_user_response.text)
        assert_user_not_found_response(actual=get_user_response_data)
        validate_json_schema(instance=get_user_response.json(), schema=InternalErrorResponseSchema.model_json_schema())

    @allure.tag(AllureTag.CREATE_ENTITY)
    @allure.story(AllureStory.CREATE_ENTITY)
    @allure.sub_suite(AllureStory.CREATE_ENTITY)
    @allure.title("Create user with existing email")
    @allure.severity(Severity.CRITICAL)
    def test_create_user_with_existing_email(
        self,
        public_users_client: PublicUsersClient,
        private_users_client: PrivateUsersClient,
        function_user: UserFixture,
        authentication_client: AuthenticationClient,
        user_request_with_existing_email: CreateUserRequestSchema,
    ) -> None:
        """Проверяет запрет создания пользователя с существующим email.

        Передает email созданного пользователя и отличающиеся остальные
        данные. Проверяет ошибку, сохранность профиля через GET и возможность
        входа с исходным паролем.

        Args:
            public_users_client: Фикстура публичного API-клиента пользователей.
            private_users_client: Фикстура авторизованного API-клиента пользователей.
            function_user: Фикстура с исходными данными созданного пользователя.
            authentication_client: Фикстура API-клиента аутентификации.
            user_request_with_existing_email: Тот же email и отличающиеся остальные данные.

        Raises:
            AssertionError: Если HTTP-статус, сообщение, структура ошибки
                или сохраненные данные пользователя, включая пароль,
                не соответствуют ожиданиям.
        """
        original_create_user_request = function_user.request
        create_user_request = user_request_with_existing_email
        create_user_response = public_users_client.create_user_api(request=create_user_request)

        assert_status_code(actual=create_user_response.status_code, expected=HTTPStatus.FORBIDDEN)
        create_user_response_data = InternalErrorResponseSchema.model_validate_json(create_user_response.text)
        assert_user_with_existing_email_response(actual=create_user_response_data, email=create_user_request.email)
        validate_json_schema(
            instance=create_user_response.json(), schema=InternalErrorResponseSchema.model_json_schema()
        )

        get_user_response = private_users_client.get_user_api(user_id=function_user.response.user.id)

        assert_status_code(actual=get_user_response.status_code, expected=HTTPStatus.OK)
        get_user_response_data = GetUserResponseSchema.model_validate_json(get_user_response.text)
        assert_user(actual=get_user_response_data.user, expected=function_user.response.user)
        validate_json_schema(instance=get_user_response.json(), schema=GetUserResponseSchema.model_json_schema())

        login_request = LoginRequestSchema(
            email=original_create_user_request.email, password=original_create_user_request.password
        )
        login_response = authentication_client.login_api(request=login_request)

        assert_status_code(actual=login_response.status_code, expected=HTTPStatus.OK)
        login_response_data = LoginResponseSchema.model_validate_json(login_response.text)
        assert_login_response(response=login_response_data)
        validate_json_schema(instance=login_response.json(), schema=LoginResponseSchema.model_json_schema())
