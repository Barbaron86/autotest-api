from shlex import quote

from httpx import Request, RequestNotRead


def make_curl_from_request(request: Request) -> str:
    """Формирует cURL-команду для HTTP-запроса.

    Экранирует аргументы для Bash и других POSIX-совместимых оболочек.
    Потоковое или бинарное тело не включается в команду: чтение потока
    могло бы повлиять на отправку запроса, а бинарные данные не являются текстом.
    Длину тела вычисляет cURL, поэтому Content-Length не копируется.

    Args:
        request: Подготовленный HTTP-запрос с URL, заголовками и телом.

    Returns:
        Многострочная cURL-команда с доступным текстовым телом запроса.
    """
    parts = [f"curl --request {quote(request.method)}", quote(str(request.url))]
    for header, value in request.headers.multi_items():
        if header.lower() == "content-length":
            continue
        curl_header = f"{header}: {value}" if value else f"{header};"
        parts.append(f"--header {quote(curl_header)}")

    try:
        body = request.content.decode("utf-8")
    except (RequestNotRead, UnicodeDecodeError):
        body = ""

    if body:
        parts.append(f"--data-raw {quote(body)}")

    return " \\\n  ".join(parts)
