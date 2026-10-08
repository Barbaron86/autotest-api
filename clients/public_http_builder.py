from httpx import Client

from clients.event_hooks import curl_event_hook
from config import settings


def get_public_http_client() -> Client:
    """Создает HTTP-клиент для публичных API-методов.

    Returns:
        HTTP-клиент без заголовка авторизации.
    """
    return Client(
        base_url=str(settings.base_url),
        timeout=settings.timeout,
        event_hooks={"request": [curl_event_hook]},
    )
