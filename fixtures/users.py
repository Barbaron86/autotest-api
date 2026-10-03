"""Фикстуры API-клиентов и тестовых пользователей."""

from collections.abc import Iterator

import pytest
from pydantic import BaseModel, EmailStr

from clients.private_http_builder import AuthenticationUserSchema
from clients.users.private_users_client import PrivateUsersClient, get_private_users_client
from clients.users.public_users_client import PublicUsersClient, get_public_users_client
from clients.users.user_schema import CreateUserRequestSchema, CreateUserResponseSchema


class UserFixture(BaseModel):
    """Данные пользователя, созданного фикстурой.

    Attributes:
        request: Запрос на создание пользователя с его учетными данными.
        response: Ответ API с данными созданного пользователя.
    """

    request: CreateUserRequestSchema
    response: CreateUserResponseSchema

    @property
    def email(self) -> EmailStr:
        """Возвращает email пользователя.

        Returns:
            Email из запроса на создание пользователя.
        """
        return self.request.email

    @property
    def password(self) -> str:
        """Возвращает пароль пользователя.

        Returns:
            Пароль из запроса на создание пользователя.
        """
        return self.request.password

    @property
    def authentication_user(self) -> AuthenticationUserSchema:
        """Формирует учетные данные для авторизации API-клиентов.

        Returns:
            Модель с email и паролем созданного пользователя.
        """
        return AuthenticationUserSchema(email=self.email, password=self.password)


@pytest.fixture
def public_users_client() -> Iterator[PublicUsersClient]:
    """Создает публичный клиент пользователей для одного теста.

    Закрывает HTTP-соединения при завершении фикстуры.

    Yields:
        API-клиент для работы с публичными методами пользователей.
    """
    client = get_public_users_client()
    with client.client:
        yield client


@pytest.fixture
def function_user(public_users_client: PublicUsersClient) -> UserFixture:
    """Создает нового пользователя для одного теста.

    Args:
        public_users_client: Фикстура публичного API-клиента пользователей.

    Returns:
        Данные запроса на создание пользователя и ответа API.
    """
    request = CreateUserRequestSchema()
    response = public_users_client.create_user(request=request)
    return UserFixture(request=request, response=response)


@pytest.fixture
def private_users_client(function_user: UserFixture) -> Iterator[PrivateUsersClient]:
    """Создает авторизованный клиент пользователей для одного теста.

    Использует учетные данные созданного пользователя и закрывает
    HTTP-соединения при завершении фикстуры.

    Args:
        function_user: Фикстура с данными созданного пользователя.

    Yields:
        API-клиент для работы с приватными методами пользователей.
    """
    client = get_private_users_client(user=function_user.authentication_user)
    with client.client:
        yield client
