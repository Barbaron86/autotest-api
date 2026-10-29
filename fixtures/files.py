from collections.abc import Iterator

import pytest
from pydantic import BaseModel

from clients.files.files_client import FilesClient, get_files_client
from clients.files.files_schema import CreateFileRequestSchema, CreateFileResponseSchema
from config import settings
from fixtures.users import UserFixture
from tools.assertions.files import assert_create_file_response


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
def file_request_with_too_long_filename() -> CreateFileRequestSchema:
    """Подготавливает запрос с именем на один символ длиннее лимита API.

    Returns:
        Запрос с именем из 256 ASCII-символов при допустимой длине до 255.
    """
    return CreateFileRequestSchema(filename="a" * 256)


@pytest.fixture
def function_file(files_client: FilesClient) -> FileFixture:
    """Загружает тестовый файл для одного теста.

    Args:
        files_client: Фикстура авторизованного API-клиента файлов.

    Returns:
        Запрос и ответ загрузки файла, проверенный по полям запроса.

    Raises:
        AssertionError: Если данные загруженного файла не соответствуют запросу.
    """
    request = CreateFileRequestSchema(upload_file=settings.test_data.image_png_file)
    response = files_client.create_file(request=request)
    assert_create_file_response(request=request, response=response)

    return FileFixture(request=request, response=response)
