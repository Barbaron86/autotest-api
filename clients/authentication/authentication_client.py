from httpx import Response

from clients.api_client import ApiClient
from clients.authentication.authentication_schema import LoginRequestSchema, LoginResponseSchema, RefreshRequestSchema
from clients.public_http_builder import get_public_http_client


class AuthenticationClient(ApiClient):
    """API-клиент для работы с аутентификацией."""

    def login_api(self, request: LoginRequestSchema) -> Response:
        """Выполняет запрос на аутентификацию пользователя.

        Args:
            request: Данные для аутентификации.

        Returns:
            HTTP-ответ API на запрос аутентификации.
        """
        return self.post("/api/v1/authentication/login", json=request.model_dump())

    def refresh_api(self, request: RefreshRequestSchema) -> Response:
        """Выполняет запрос на обновление токена.

        Args:
            request: Данные для обновления токена.

        Returns:
            HTTP-ответ API на запрос обновления токена.
        """
        return self.post("/api/v1/authentication/refresh", json=request.model_dump())

    def login(self, request: LoginRequestSchema) -> LoginResponseSchema:
        """Аутентифицирует пользователя.

        Args:
            request: Данные для аутентификации.

        Returns:
            Данные авторизации.
        """
        response = self.login_api(request)
        response.raise_for_status()

        return LoginResponseSchema.model_validate_json(response.text)


def get_authentication_client() -> AuthenticationClient:
    """Создает публичный API-клиент для аутентификации.

    Returns:
        Экземпляр AuthenticationClient.
    """
    return AuthenticationClient(client=get_public_http_client())
