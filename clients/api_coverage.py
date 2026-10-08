"""Общий трекер покрытия API с типизированным декоратором для HTTPX."""

from collections.abc import Callable
from typing import cast

from httpx import Response
from swagger_coverage_tool import SwaggerCoverageTracker


class APICoverageTracker:
    """Сохраняет типы клиентских методов при подключении трекера библиотеки."""

    def __init__(self, service: str) -> None:
        """Создаёт библиотечный трекер для настроенного сервиса.

        Args:
            service: Ключ сервиса из SWAGGER_COVERAGE_SERVICES.

        Raises:
            ValueError: Если сервис отсутствует в настройках библиотеки.
        """
        self._tracker = SwaggerCoverageTracker(service=service)

    def track_coverage_httpx[**P](self, endpoint: str) -> Callable[[Callable[P, Response]], Callable[P, Response]]:
        """Возвращает декоратор библиотеки с сохранением сигнатуры метода.

        Args:
            endpoint: Шаблон пути в точном соответствии с OpenAPI.

        Returns:
            Декоратор, записывающий покрытие и возвращающий исходный HTTP-ответ.
        """
        return cast(
            Callable[[Callable[P, Response]], Callable[P, Response]],
            self._tracker.track_coverage_httpx(endpoint),
        )


tracker = APICoverageTracker(service="api-course")
