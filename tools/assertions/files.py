from clients.error_schema import InternalErrorResponseSchema, ValidationErrorResponseSchema, ValidationErrorSchema
from clients.files.files_schema import (
    CreateFileRequestSchema,
    CreateFileResponseSchema,
    FileSchema,
    GetFileResponseSchema,
)
from tools.assertions.base import assert_equal
from tools.assertions.errors import assert_internal_error_response, assert_validation_error_response


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

    assert_equal(str(response.file.url), expected_url, "url")
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


def assert_create_file_with_empty_filename_response(actual: ValidationErrorResponseSchema) -> None:
    """Проверяет ошибку валидации при загрузке файла с пустым именем.

    Args:
        actual: Фактический ответ API с ошибками валидации.

    Raises:
        AssertionError: Если ответ не соответствует ошибке пустого имени файла.
    """
    expected = ValidationErrorResponseSchema(
        detail=[
            ValidationErrorSchema(
                type="string_too_short",
                input="",
                context={"min_length": 1},
                message="String should have at least 1 character",
                location=["body", "filename"],
            )
        ]
    )
    assert_validation_error_response(actual=actual, expected=expected)


def assert_create_file_with_empty_directory_response(actual: ValidationErrorResponseSchema) -> None:
    """Проверяет ошибку валидации при загрузке файла с пустой директорией.

    Args:
        actual: Фактический ответ API с ошибками валидации.

    Raises:
        AssertionError: Если ответ не соответствует ошибке пустой директории.
    """
    expected = ValidationErrorResponseSchema(
        detail=[
            ValidationErrorSchema(
                type="string_too_short",
                input="",
                context={"min_length": 1},
                message="String should have at least 1 character",
                location=["body", "directory"],
            )
        ]
    )
    assert_validation_error_response(actual=actual, expected=expected)


def assert_file_not_found_response(actual: InternalErrorResponseSchema) -> None:
    """Проверяет сообщение API об отсутствии файла.

    Args:
        actual: Фактический ответ API с сообщением об ошибке.

    Raises:
        AssertionError: Если ответ не содержит сообщение «File not found».
    """
    expected = InternalErrorResponseSchema(detail="File not found")
    assert_internal_error_response(actual=actual, expected=expected)


def assert_get_file_with_incorrect_file_id_response(actual: ValidationErrorResponseSchema) -> None:
    """Проверяет ошибку валидации идентификатора «incorrect-file-id».

    Args:
        actual: Фактический ответ API с ошибками валидации.

    Raises:
        AssertionError: Если ответ не соответствует ошибке разбора UUID
            в параметре пути file_id.
    """
    error = "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1"
    expected = ValidationErrorResponseSchema(
        detail=[
            ValidationErrorSchema(
                type="uuid_parsing",
                input="incorrect-file-id",
                context={"error": error},
                message=f"Input should be a valid UUID, {error}",
                location=["path", "file_id"],
            )
        ]
    )
    assert_validation_error_response(actual=actual, expected=expected)
