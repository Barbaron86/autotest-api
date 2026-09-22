from typing import TypedDict

from httpx import Response

from clients.api_client import ApiClient


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
