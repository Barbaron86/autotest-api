from clients.files.files_schema import (
    CreateFileRequestSchema,
    CreateFileResponseSchema,
    FileSchema,
    GetFileResponseSchema,
)
from tools.assertions.base import assert_equal


def assert_create_file_response(request: CreateFileRequestSchema, response: CreateFileResponseSchema) -> None:
    """Проверяет соответствие данных загруженного файла исходному запросу.

    Args:
        request: Данные запроса на загрузку файла.
        response: Ответ API с данными загруженного файла.

    Raises:
        AssertionError: Если URL, имя файла или директория
            не соответствуют ожидаемым значениям.
    """
    expected_url = f"http://localhost:8000/static/{request.directory}/{request.filename}"

    assert_equal(response.file.url, expected_url, "url")
    assert_equal(response.file.filename, request.filename, "filename")
    assert_equal(response.file.directory, request.directory, "directory")


def assert_file(actual: FileSchema, expected: FileSchema) -> None:
    """Проверяет соответствие фактических данных файла ожидаемым.

    Args:
        actual: Фактические данные файла из ответа API.
        expected: Ожидаемые данные файла.

    Raises:
        AssertionError: Если идентификатор, URL, имя файла
            или директория не соответствуют ожидаемым значениям.
    """
    assert_equal(actual.id, expected.id, "id")
    assert_equal(actual.url, expected.url, "url")
    assert_equal(actual.filename, expected.filename, "filename")
    assert_equal(actual.directory, expected.directory, "directory")


def assert_get_file_response(
    get_file_response: GetFileResponseSchema, create_file_response: CreateFileResponseSchema
) -> None:
    """Проверяет ответ получения файла по данным его создания.

    Args:
        get_file_response: Ответ API на запрос получения файла.
        create_file_response: Ответ API, полученный при создании файла.

    Raises:
        AssertionError: Если данные полученного файла
            не соответствуют данным созданного файла.
    """

    assert_file(get_file_response.file, create_file_response.file)
