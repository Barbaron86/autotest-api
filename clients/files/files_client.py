from typing import TypedDict

from httpx import Response

from clients.api_client import ApiClient


class CreateFileRequestDict(TypedDict):
    """Описание структуры запроса на создание файла."""

    filename: str
    directory: str
    upload_file: str


class FilesClient(ApiClient):
    """API-клиент для работы с файлами."""

    def create_file_api(self, request: CreateFileRequestDict) -> Response:
        """
        Загружает файл на сервер.

        Args:
            request: Данные для загрузки файла, включая имя файла,
                директорию и путь к локальному файлу.

        Returns:
            HTTP-ответ API на запрос загрузки файла.
        """
        return self.post("/api/v1/files", data=request, files={"upload_file": open(request["upload_file"], "rb")})

    def get_file_api(self, file_id: str) -> Response:
        """
        Получает файл с сервера по его идентификатору.л

        Args:
            file_id: Идентификатор файла.

        Returns:
            HTTP-ответ API на запрос получения файла.
        """
        return self.get(f"/api/v1/files/{file_id}")

    def delete_file_api(self, file_id: str) -> Response:
        """
        Удаляет файл с сервера по его идентификатору.

        Args:
            file_id: Идентификатор файла.

        Returns:
            HTTP-ответ API на запрос удаления файла.
        """
        return self.delete(f"/api/v1/files/{file_id}")
