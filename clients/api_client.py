from collections.abc import Mapping
from typing import Any

import allure
from httpx import URL, Client, Response


class ApiClient:
    """Базовый API-клиент для выполнения HTTP-запросов."""

    def __init__(self, client: Client):
        """Инициализирует API-клиент.

        Args:
            client: Экземпляр httpx.Client для выполнения HTTP-запросов.
        """
        self.client = client

    @allure.step("Make GET request to {url}")
    def get(self, url: URL | str, params: Mapping[str, Any] | None = None) -> Response:
        """Выполняет GET-запрос.

        Args:
            url: URL-адрес эндпоинта.
            params: Query-параметры запроса.

        Returns:
            HTTP-ответ сервера.
        """
        return self.client.get(url=url, params=params)

    @allure.step("Make POST request to {url}")
    def post(
        self,
        url: URL | str,
        json: Any | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, Any] | None = None,
    ) -> Response:
        """Выполняет POST-запрос.

        Args:
            url: URL-адрес эндпоинта.
            json: Данные тела запроса в формате JSON.
            data: Данные формы.
            files: Файлы для загрузки.

        Returns:
            HTTP-ответ сервера.
        """
        return self.client.post(url=url, json=json, data=data, files=files)

    @allure.step("Make PATCH request to {url}")
    def patch(self, url: URL | str, json: Any | None = None) -> Response:
        """Выполняет PATCH-запрос.

        Args:
            url: URL-адрес эндпоинта.
            json: Данные тела запроса в формате JSON.

        Returns:
            HTTP-ответ сервера.
        """
        return self.client.patch(url=url, json=json)

    @allure.step("Make DELETE request to {url}")
    def delete(self, url: URL | str) -> Response:
        """Выполняет DELETE-запрос.

        Args:
            url: URL-адрес эндпоинта.

        Returns:
            HTTP-ответ сервера.
        """
        return self.client.delete(url=url)
