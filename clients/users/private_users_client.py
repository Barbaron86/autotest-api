import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.private_http_builder import AuthenticationUserSchema, get_private_http_client
from clients.users.user_schema import GetUserResponseSchema, UpdateUserRequestSchema
from tools.routes import APIRoutes


class PrivateUsersClient(ApiClient):
    """API-клиент для работы с приватными методами пользователей."""

    @allure.step("Get user me")
    def get_user_me_api(self) -> Response:
        """Выполняет запрос на получение текущего пользователя.

        Returns:
            HTTP-ответ API с данными текущего пользователя.
        """
        return self.get(f"{APIRoutes.USERS}/me")

    @allure.step("Get user by id {user_id}")
    def get_user_api(self, user_id: str) -> Response:
        """Выполняет запрос на получение пользователя по идентификатору.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            HTTP-ответ API с данными пользователя.
        """
        return self.get(f"{APIRoutes.USERS}/{user_id}")

    def get_user(self, user_id: str) -> GetUserResponseSchema:
        """Получает пользователя по идентификатору.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Данные пользователя.
        """
        response = self.get_user_api(user_id=user_id)
        response.raise_for_status()

        return GetUserResponseSchema.model_validate_json(response.text)

    @allure.step("Delete user by id {user_id}")
    def delete_user_api(self, user_id: str) -> Response:
        """Выполняет запрос на удаление пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            HTTP-ответ API на запрос удаления пользователя.
        """
        return self.delete(f"{APIRoutes.USERS}/{user_id}")

    @allure.step("Update user by id {user_id}")
    def update_user_api(self, user_id: str, request: UpdateUserRequestSchema) -> Response:
        """Выполняет запрос на обновление пользователя.

        Args:
            user_id: Идентификатор пользователя.
            request: Данные для обновления пользователя.

        Returns:
            HTTP-ответ API на запрос обновления пользователя.
        """
        return self.patch(f"{APIRoutes.USERS}/{user_id}", json=request.model_dump(exclude_unset=True))


def get_private_users_client(user: AuthenticationUserSchema) -> PrivateUsersClient:
    """Создает авторизованный API-клиент для работы с пользователями.

    Args:
        user: Учетные данные пользователя для аутентификации.

    Returns:
        Авторизованный экземпляр PrivateUsersClient.
    """
    return PrivateUsersClient(client=get_private_http_client(user))
