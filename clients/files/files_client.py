from typing import TypedDict

from httpx import Response

from clients.api_client import ApiClient
from clients.private_http_builder import AuthenticationUserDict, get_private_http_client


class FileDict(TypedDict):
    """Описание структуры данных файла."""

    id: str
    filename: str
    directory: str
    url: str


class CreateFileRequestDict(TypedDict):
    """Описание структуры запроса на создание файла."""

    filename: str
    directory: str
    upload_file: str


class CreateFileResponseDict(TypedDict):
    """Описание структуры ответа на запрос создания файла."""

    file: FileDict


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

    def create_file(self, request: CreateFileRequestDict) -> CreateFileResponseDict:
        """
        Загружает файл на сервер и возвращает данные о загруженном файле.

        Args:
            request: Данные для загрузки файла, включая имя файла,
                директорию и путь к локальному файлу.

        Returns:
            Данные загруженного файла в виде словаря.
        """
        response = self.create_file_api(request=request)
        response.raise_for_status()

        response_data: CreateFileResponseDict = response.json()
        return response_data

    def get_file_api(self, file_id: str) -> Response:
        """
        Получает файл с сервера по его идентификатору.

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


def get_files_client(user: AuthenticationUserDict) -> FilesClient:
    """Функция для получения экземпляра FilesClient.

    Args:
        user: Учетные данные пользователя для аутентификации.

    Returns:
        Экземпляр FilesClient.
    """
    return FilesClient(client=get_private_http_client(user))
