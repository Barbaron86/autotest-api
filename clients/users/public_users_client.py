from typing import TypedDict

from httpx import Response

from clients.api_client import ApiClient
from clients.public_http_builder import get_public_http_client


class CreateUserDict(TypedDict):
    """Описание структуры запроса на создание пользователя."""

    email: str
    password: str
    lastName: str
    firstName: str
    middleName: str


class PublicUsersClient(ApiClient):
    """API-клиент для работы с публичными методами пользователей."""

    def create_user_api(self, request: CreateUserDict) -> Response:
        """Создает нового пользователя.

        Args:
            request: Данные нового пользователя.

        Returns:
            HTTP-ответ API на запрос создания пользователя.
        """
        return self.post("/api/v1/users", json=request)


def get_public_users_client() -> PublicUsersClient:
    """Функция для получения экземпляра PublicUsersClient.

    Returns:
        Экземпляр PublicUsersClient.
    """
    return PublicUsersClient(client=get_public_http_client())
