from httpx import Client


def get_public_http_client() -> Client:
    """Создает HTTP-клиент для публичных API-методов.

    Returns:
        HTTP-клиент без заголовка авторизации.
    """
    return Client(base_url="http://localhost:8000", timeout=100)
