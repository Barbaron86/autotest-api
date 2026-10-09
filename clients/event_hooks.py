import allure
from httpx import Request, Response
from loguru import logger

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


def log_request_event_hook(request: Request) -> None:
    """Записывает метод и адрес отправляемого HTTP-запроса.

    Args:
        request: Подготовленный запрос HTTPX.
    """
    url = request.url.copy_with(username=None, password=None, query=None, fragment=None)
    logger.info("→ {} {}", request.method, url)


def log_response_event_hook(response: Response) -> None:
    """Записывает статус и адрес полученного HTTP-ответа.

    Args:
        response: Ответ HTTPX.
    """
    logger.info(
        "← {} {} {} {}",
        response.status_code,
        response.reason_phrase,
        response.request.method,
        response.url.path,
    )
