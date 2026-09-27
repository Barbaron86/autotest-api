from httpx import Client
from pydantic import EmailStr

from clients.authentication.authentication_client import get_authentication_client
from clients.authentication.authentication_schema import LoginRequestSchema
from clients.base_schema import BaseSchema


class AuthenticationUserSchema(BaseSchema):
    """Учетные данные пользователя для аутентификации."""

    email: EmailStr
    password: str


def get_private_http_client(user: AuthenticationUserSchema) -> Client:
    """Создает авторизованный HTTP-клиент для приватных API-методов.

    Args:
        user: Учетные данные пользователя для аутентификации.

    Returns:
        Авторизованный HTTP-клиент.
    """
    authentication_client = get_authentication_client()
    login_request = LoginRequestSchema(email=user.email, password=user.password)
    login_response = authentication_client.login(login_request)

    return Client(
        base_url="http://localhost:8000",
        timeout=100,
        headers={"Authorization": f"Bearer {login_response.token.access_token}"},
    )
