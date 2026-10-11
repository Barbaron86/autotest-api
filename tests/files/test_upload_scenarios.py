from http import HTTPStatus
from uuid import uuid4

import allure
import pytest

from clients.error_schema import ValidationErrorResponseSchema
from clients.files.files_client import FilesClient
from clients.files.files_schema import CreateFileRequestSchema, CreateFileResponseSchema
from tools.assertions.base import assert_status_code
from tools.assertions.files import assert_create_file_response, assert_create_file_with_empty_directory_response
from tools.assertions.schema import validate_json_schema


@pytest.mark.files
@pytest.mark.regression
class TestUploadScenarios:
    @allure.title("Upload file with custom metadata")
    def test_upload_with_custom_metadata(self, files_client: FilesClient) -> None:
        request = CreateFileRequestSchema(filename=f"upload-{uuid4()}.png", directory="review")
        response = files_client.create_file_api(request=request)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = CreateFileResponseSchema.model_validate_json(response.text)
        assert_create_file_response(request=request, response=response_data)
        validate_json_schema(response.json(), CreateFileResponseSchema.model_json_schema())

    @allure.title("Reject upload with empty directory")
    def test_upload_with_empty_directory(self, files_client: FilesClient) -> None:
        request = CreateFileRequestSchema(directory="")
        response = files_client.create_file_api(request=request)

        assert_status_code(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        response_data = ValidationErrorResponseSchema.model_validate_json(response.text)
        assert_create_file_with_empty_directory_response(actual=response_data)
        validate_json_schema(response.json(), ValidationErrorResponseSchema.model_json_schema())

    @allure.title("Reject upload with empty filename")
    def test_upload_with_empty_filename(self, files_client: FilesClient) -> None:
        request = CreateFileRequestSchema(filename="")
        response = files_client.create_file_api(request=request)

        assert_status_code(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        response_data = ValidationErrorResponseSchema.model_validate_json(response.text)
        assert_create_file_with_empty_directory_response(actual=response_data)
        validate_json_schema(response.json(), ValidationErrorResponseSchema.model_json_schema())
