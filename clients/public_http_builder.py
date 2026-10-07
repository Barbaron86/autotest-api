from httpx import Client

from config import settings


def get_public_http_client() -> Client:
    """Создает HTTP-клиент для публичных API-методов.

    Returns:
        HTTP-клиент без заголовка авторизации.
    """
    return Client(base_url=str(settings.base_url), timeout=settings.timeout)
