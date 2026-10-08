import allure
from httpx import Request

from tools.http.curl import make_curl_from_request


def curl_event_hook(request: Request) -> None:
    """Прикрепляет cURL-команду к текущему шагу Allure перед отправкой запроса.

    Args:
        request: Подготовленный запрос HTTPX.
    """
    allure.attach(
        body=make_curl_from_request(request),
        name="cURL command",
        attachment_type=allure.attachment_type.TEXT,
    )
