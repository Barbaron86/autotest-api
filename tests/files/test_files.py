from http import HTTPStatus

import pytest

from clients.files.files_client import FilesClient
from clients.files.files_schema import CreateFileRequestSchema, CreateFileResponseSchema, GetFileResponseSchema
from fixtures.files import FileFixture
from tools.assertions.base import assert_status_code
from tools.assertions.files import assert_create_file_response, assert_get_file_response
from tools.assertions.schema import validate_json_schema


@pytest.mark.files
@pytest.mark.regression
class TestFiles:
    """Регрессионные тесты API для работы с файлами."""

    def test_create_file(self, files_client: FilesClient):
        """Проверяет успешную загрузку файла.

        Загружает тестовый файл и проверяет HTTP-статус,
        соответствие данных ответа исходному запросу
        и структуру ответа по JSON Schema.

        Args:
            files_client: Фикстура авторизованного API-клиента файлов.

        Raises:
            AssertionError: Если HTTP-статус или данные загруженного
                файла не соответствуют ожидаемым значениям.
        """
        request = CreateFileRequestSchema()
        response = files_client.create_file_api(request)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = CreateFileResponseSchema.model_validate_json(response.text)

        assert_create_file_response(request=request, response=response_data)

        validate_json_schema(response.json(), response_data.model_json_schema())

    def test_get_file(self, files_client: FilesClient, function_file: FileFixture):
        """Проверяет успешное получение ранее загруженного файла.

        Получает файл по идентификатору, созданному фикстурой,
        и проверяет HTTP-статус, соответствие данных полученного файла
        данным при его создании и структуру ответа по JSON Schema.

        Args:
            files_client: Фикстура авторизованного API-клиента файлов.
            function_file: Фикстура с данными ранее загруженного файла.

        Raises:
            AssertionError: Если HTTP-статус или данные полученного
                файла не соответствуют ожидаемым значениям.
        """

        file_id = function_file.response.file.id
        response = files_client.get_file_api(file_id)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = GetFileResponseSchema.model_validate_json(response.text)

        assert_get_file_response(get_file_response=response_data, create_file_response=function_file.response)
        validate_json_schema(response.json(), response_data.model_json_schema())
