from typing import TypedDict

from httpx import Client

from clients.authentication.authentication_client import LoginRequestDict, get_authentication_client


class AuthenticationUserDict(TypedDict):
    """Описывает учетные данные пользователя для аутентификации."""

    email: str
    password: str


def get_private_http_client(user: AuthenticationUserDict) -> Client:
    """Создает авторизованный HTTP-клиент для приватных API-методов.

    Args:
        user: Учетные данные пользователя для аутентификации.

    Returns:
        HTTP-клиент с заголовком авторизации.
    """
    authentication_client = get_authentication_client()
    login_request = LoginRequestDict(email=user["email"], password=user["password"])
    login_response = authentication_client.login(login_request)

    return Client(
        base_url="http://localhost:8000",
        timeout=100,
        headers={"Authorization": f"Bearer {login_response['token']['accessToken']}"},
    )
