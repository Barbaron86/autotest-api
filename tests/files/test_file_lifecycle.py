from http import HTTPStatus

import allure
import pytest

from clients.files.files_client import FilesClient
from clients.files.files_schema import GetFileResponseSchema
from fixtures.files import FileFixture
from tools.assertions.base import assert_status_code
from tools.assertions.files import assert_get_file_response
from tools.assertions.schema import validate_json_schema


@pytest.mark.files
@pytest.mark.regression
class TestFileLifecycle:
    @allure.title("Read uploaded file")
    def test_read_uploaded_file(self, files_client: FilesClient, function_file: FileFixture) -> None:
        response = files_client.get_file_api(file_id=function_file.response.file.id)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = GetFileResponseSchema.model_validate_json(response.text)
        assert_get_file_response(get_file_response=response_data, create_file_response=function_file.response)
        validate_json_schema(response.json(), GetFileResponseSchema.model_json_schema())

    @allure.title("Read file with default metadata")
    def test_read_file_with_default_metadata(self, files_client: FilesClient, function_file: FileFixture) -> None:
        response = files_client.get_file_api(file_id=function_file.response.file.id)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = GetFileResponseSchema.model_validate_json(function_file.response.model_dump_json())
        assert_get_file_response(get_file_response=response_data, create_file_response=function_file.response)
        validate_json_schema(response_data.model_dump(mode="json"), GetFileResponseSchema.model_json_schema())

    @allure.title("Deleted file is no longer available")
    def test_deleted_file_is_unavailable(self, files_client: FilesClient, function_file: FileFixture) -> None:
        file_id = function_file.response.file.id
        get_response = files_client.get_file_api(file_id=file_id)
        assert_status_code(get_response.status_code, HTTPStatus.OK)

        delete_response = files_client.delete_file_api(file_id=file_id)
        assert_status_code(delete_response.status_code, HTTPStatus.OK)
        assert_status_code(get_response.status_code, HTTPStatus.NOT_FOUND)
