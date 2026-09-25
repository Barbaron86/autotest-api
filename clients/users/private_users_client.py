from typing import TypedDict

from httpx import Response

from clients.api_client import ApiClient
from clients.private_http_builder import AuthenticationUserDict, get_private_http_client


class UserUpdateRequestDict(TypedDict):
    """Описание структуры запроса на обновление информации о пользователе."""

    email: str | None
    lastName: str | None
    firstName: str | None
    middleName: str | None


class PrivateUsersClient(ApiClient):
    def get_user_me_api(self) -> Response:
        """
        Метод получает информацию о текущем пользователе.

        Returns:
            Ответ от сервера в виде объекта httpx.Response.
        """
        return self.get("/api/v1/users/me")

    def get_user_api(self, user_id: str) -> Response:
        """
        Метод получает информацию о пользователе по его идентификатору.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Ответ от сервера в виде объекта httpx.Response.
        """
        return self.get(f"/api/v1/users/{user_id}")

    def delete_user_api(self, user_id: str) -> Response:
        """
        Метод удаляет пользователя по его идентификатору.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Ответ от сервера в виде объекта httpx.Response.
        """
        return self.delete(f"/api/v1/users/{user_id}")

    def update_user_api(self, user_id: str, request: UserUpdateRequestDict) -> Response:
        """
        Метод обновляет информацию о пользователе по его идентификатору.

        Args:
            user_id: Идентификатор пользователя.
            request: Данные для обновления пользователя.

        Returns:
            Ответ от сервера в виде объекта httpx.Response.
        """
        return self.patch(f"/api/v1/users/{user_id}", json=request)


def get_private_users_client(user: AuthenticationUserDict) -> PrivateUsersClient:
    """Создает клиент для работы с приватными методами пользователей.

    Args:
        user: Учетные данные пользователя для аутентификации.

    Returns:
        Экземпляр PrivateUsersClient с авторизованным HTTP-клиентом.
    """
    return PrivateUsersClient(client=get_private_http_client(user))
