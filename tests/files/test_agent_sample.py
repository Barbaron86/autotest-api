from http import HTTPStatus

import allure
import pytest

from clients.files.files_client import FilesClient
from clients.files.files_schema import CreateFileRequestSchema, CreateFileResponseSchema
from tools.allure.features import AllureFeature
from tools.assertions.base import assert_status_code
from tools.assertions.files import assert_create_file_response


@pytest.mark.files
@pytest.mark.regression
@allure.feature(AllureFeature.FILES)
class TestFileUpload:
    @allure.title("Upload file with custom metadata")
    def test_create_file_with_custom_metadata(self, files_client: FilesClient) -> None:
        request = CreateFileRequestSchema(filename="review-sample.png", directory="review")
        response = files_client.create_file_api(request=request)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = CreateFileResponseSchema.model_validate_json(response.text)
        assert_create_file_response(request=request, response=response_data)

    @allure.title("Upload file with default metadata")
    def test_create_file_with_default_metadata(self, files_client: FilesClient) -> None:
        request = CreateFileRequestSchema()
        response = files_client.create_file_api(payload=request)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = CreateFileResponseSchema.model_validate_json(response.text)
        assert_create_file_response(request=request, response=response_data)
