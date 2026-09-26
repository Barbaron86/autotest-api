from typing import TypedDict

from httpx import Response

from clients.api_client import ApiClient
from clients.public_http_builder import get_public_http_client


class UserDict(TypedDict):
    """Описание структуры данных пользователя."""

    id: str
    email: str
    lastName: str
    firstName: str
    middleName: str


class CreateUserRequestDict(TypedDict):
    """Описание структуры запроса на создание пользователя."""

    email: str
    password: str
    lastName: str
    firstName: str
    middleName: str


class CreateUserResponseDict(TypedDict):
    """Описание структуры ответа на запрос создания пользователя."""

    user: UserDict


class PublicUsersClient(ApiClient):
    """API-клиент для работы с публичными методами пользователей."""

    def create_user_api(self, request: CreateUserRequestDict) -> Response:
        """Создает нового пользователя.

        Args:
            request: Данные нового пользователя.

        Returns:
            HTTP-ответ API на запрос создания пользователя.
        """
        return self.post("/api/v1/users", json=request)

    def create_user(self, request: CreateUserRequestDict) -> CreateUserResponseDict:
        """Создает нового пользователя и возвращает данные пользователя.

        Args:
            request: Данные нового пользователя.

        Returns:
            Данные созданного пользователя в виде словаря.
        """
        response = self.create_user_api(request=request)
        response.raise_for_status()

        response_data: CreateUserResponseDict = response.json()
        return response_data


def get_public_users_client() -> PublicUsersClient:
    """Функция для получения экземпляра PublicUsersClient.

    Returns:
        Экземпляр PublicUsersClient.
    """
    return PublicUsersClient(client=get_public_http_client())
