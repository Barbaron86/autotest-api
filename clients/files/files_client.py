import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.api_coverage import tracker
from clients.files.files_schema import CreateFileRequestSchema, CreateFileResponseSchema
from clients.private_http_builder import AuthenticationUserSchema, get_private_http_client
from tools.routes import APIRoutes


class FilesClient(ApiClient):
    """API-клиент для работы с файлами."""

    @allure.step("Create file")
    @tracker.track_coverage_httpx(APIRoutes.FILES)
    def create_file_api(self, request: CreateFileRequestSchema) -> Response:
        """Выполняет запрос на загрузку файла.

        Args:
            request: Данные для загрузки файла.

        Returns:
            HTTP-ответ API на запрос загрузки файла.
        """
        return self.post(
            APIRoutes.FILES,
            data=request.model_dump(exclude={"upload_file"}),
            files={"upload_file": request.upload_file.read_bytes()},
        )

    def create_file(self, request: CreateFileRequestSchema) -> CreateFileResponseSchema:
        """Загружает файл.

        Args:
            request: Данные для загрузки файла.

        Returns:
            Данные загруженного файла.
        """
        response = self.create_file_api(request=request)
        response.raise_for_status()

        return CreateFileResponseSchema.model_validate_json(response.text)

    @allure.step("Get file by id {file_id}")
    @tracker.track_coverage_httpx(f"{APIRoutes.FILES}/{{file_id}}")
    def get_file_api(self, file_id: str) -> Response:
        """Выполняет запрос на получение файла.

        Args:
            file_id: Идентификатор файла.

        Returns:
            HTTP-ответ API на запрос получения файла.
        """
        return self.get(f"{APIRoutes.FILES}/{file_id}")

    @allure.step("Delete file by id {file_id}")
    @tracker.track_coverage_httpx(f"{APIRoutes.FILES}/{{file_id}}")
    def delete_file_api(self, file_id: str) -> Response:
        """Выполняет запрос на удаление файла.

        Args:
            file_id: Идентификатор файла.

        Returns:
            HTTP-ответ API на запрос удаления файла.
        """
        return self.delete(f"{APIRoutes.FILES}/{file_id}")


def get_files_client(user: AuthenticationUserSchema) -> FilesClient:
    """Создает авторизованный API-клиент для работы с файлами.

    Args:
        user: Учетные данные пользователя для аутентификации.

    Returns:
        Авторизованный экземпляр FilesClient.
    """
    return FilesClient(client=get_private_http_client(user))
