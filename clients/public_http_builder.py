from httpx import Client

from clients.event_hooks import curl_event_hook, log_request_event_hook, log_response_event_hook
from config import settings


def get_public_http_client() -> Client:
    """Создает HTTP-клиент для публичных API-методов.

    Returns:
        HTTP-клиент без заголовка авторизации.
    """
    return Client(
        base_url=settings.http_client.client_url,
        timeout=settings.http_client.timeout,
        event_hooks={
            "request": [curl_event_hook, log_request_event_hook],
            "response": [log_response_event_hook],
        },
    )
