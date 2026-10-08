import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.public_http_builder import get_public_http_client
from clients.users.user_schema import CreateUserRequestSchema, CreateUserResponseSchema


class PublicUsersClient(ApiClient):
    """API-клиент для работы с публичными методами пользователей."""

    @allure.step("Create user")
    def create_user_api(self, request: CreateUserRequestSchema) -> Response:
        """Выполняет запрос на создание пользователя.

        Args:
            request: Данные для создания пользователя.

        Returns:
            HTTP-ответ API на запрос создания пользователя.
        """
        return self.post("/api/v1/users", json=request.model_dump())

    def create_user(self, request: CreateUserRequestSchema) -> CreateUserResponseSchema:
        """Создает пользователя.

        Args:
            request: Данные для создания пользователя.

        Returns:
            Данные созданного пользователя.
        """
        response = self.create_user_api(request=request)
        response.raise_for_status()

        return CreateUserResponseSchema.model_validate_json(response.text)


def get_public_users_client() -> PublicUsersClient:
    """Создает публичный API-клиент для работы с пользователями.

    Returns:
        Экземпляр PublicUsersClient.
    """
    return PublicUsersClient(client=get_public_http_client())
