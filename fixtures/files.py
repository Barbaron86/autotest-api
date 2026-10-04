from collections.abc import Iterator

import pytest
from pydantic import BaseModel

from clients.files.files_client import FilesClient, get_files_client
from clients.files.files_schema import CreateFileRequestSchema, CreateFileResponseSchema
from fixtures.users import UserFixture


class FileFixture(BaseModel):
    """Данные файла, загруженного фикстурой.

    Attributes:
        request: Запрос на загрузку файла.
        response: Ответ API с данными загруженного файла.
    """

    request: CreateFileRequestSchema
    response: CreateFileResponseSchema


@pytest.fixture
def files_client(function_user: UserFixture) -> Iterator[FilesClient]:
    """Создает авторизованный клиент файлов для одного теста.

    Использует учетные данные созданного пользователя и закрывает
    HTTP-соединения при завершении фикстуры.

    Args:
        function_user: Фикстура с данными созданного пользователя.

    Yields:
        API-клиент для работы с файлами.
    """
    files_client = get_files_client(user=function_user.authentication_user)

    with files_client.client:
        yield files_client


@pytest.fixture
def function_file(files_client: FilesClient) -> FileFixture:
    """Загружает тестовый файл для одного теста.

    Args:
        files_client: Фикстура авторизованного API-клиента файлов.

    Returns:
        Данные запроса на загрузку файла и ответа API.
    """
    request = CreateFileRequestSchema(upload_file="./testdata/files/image.png")
    response = files_client.create_file(request=request)

    return FileFixture(request=request, response=response)
