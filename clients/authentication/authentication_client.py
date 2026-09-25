from typing import TypedDict

from httpx import Response

from clients.api_client import ApiClient
from clients.public_http_builder import get_public_http_client


class LoginRequestDict(TypedDict):
    """
    Описание структуры запроса на аутентификацию.
    """

    email: str
    password: str


class RefreshRequestDict(TypedDict):
    """
    Описание структуры запроса для обновления токена.
    """

    refreshToken: str


class Token(TypedDict):
    """Описание структуры токена."""

    tokenType: str
    accessToken: str
    refreshToken: str


class LoginResponseDict(TypedDict):
    """Описание структуры ответа на запрос аутентификации."""

    token: Token


class AuthenticationClient(ApiClient):
    """Клиент для работы с /api/v1/authentication"""

    def login_api(self, request: LoginRequestDict) -> Response:
        """
        Метод выполняет аутентификацию пользователя.

        Args:
            request: Словарь с email и password.

        Returns:
            Ответ от сервера в виде объекта httpx.Response.
        """
        return self.post("/api/v1/authentication/login", json=request)

    def refresh_api(self, request: RefreshRequestDict) -> Response:
        """
        Метод обновляет токен авторизации.

        Args:
            request: Словарь с refreshToken.

        Returns:
            Ответ от сервера в виде объекта httpx.Response.
        """
        return self.post("/api/v1/authentication/refresh", json=request)

    def login(self, request: LoginRequestDict) -> LoginResponseDict:
        """Аутентифицирует пользователя и возвращает данные авторизации.

        Args:
            request: Данные пользователя для аутентификации,
                содержащие email и password.

        Returns:
            Данные ответа аутентификации, содержащие access и refresh токены.
        """
        response = self.login_api(request)
        response_data: LoginResponseDict = response.json()
        return response_data


def get_authentication_client() -> AuthenticationClient:
    """
    Функция для получения экземпляра AuthenticationClient.

    Returns:
        Экземпляр AuthenticationClient.
    """
    return AuthenticationClient(client=get_public_http_client())
