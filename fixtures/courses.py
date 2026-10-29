from collections.abc import Iterator
from http import HTTPStatus

import pytest
from pydantic import BaseModel

from clients.courses.courses_client import CoursesClient, get_courses_client
from clients.courses.courses_schema import (
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
    GetCourseResponseSchema,
)
from fixtures.files import FileFixture
from fixtures.users import UserFixture
from tools.assertions.base import assert_status_code
from tools.assertions.courses import (
    assert_course,
    assert_course_optional_fields_are_set,
    assert_create_course_response,
)
from tools.assertions.schema import validate_json_schema


class CourseFixture(BaseModel):
    """Данные курса, созданного фикстурой.

    Attributes:
        request: Запрос на создание курса.
        response: Ответ API с данными созданного курса.
    """

    request: CreateCourseRequestSchema
    response: CreateCourseResponseSchema


@pytest.fixture
def courses_client(function_user: UserFixture) -> Iterator[CoursesClient]:
    """Создает авторизованный клиент курсов для одного теста.

    Использует учетные данные созданного пользователя и закрывает
    HTTP-соединения при завершении фикстуры.

    Args:
        function_user: Фикстура с данными созданного пользователя.

    Yields:
        API-клиент для работы с курсами.
    """
    courses_client = get_courses_client(user=function_user.authentication_user)

    with courses_client.client:
        yield courses_client


@pytest.fixture
def function_course(
    courses_client: CoursesClient,
    function_user: UserFixture,
    function_file: FileFixture,
) -> CourseFixture:
    """Создает новый курс для одного теста.

    Использует созданного пользователя и загруженный файл
    для формирования запроса на создание курса.

    Args:
        courses_client: Фикстура авторизованного API-клиента курсов.
        function_user: Фикстура с данными созданного пользователя.
        function_file: Фикстура с данными загруженного файла.

    Returns:
        Запрос и ответ создания курса, проверенный по полям запроса.

    Raises:
        AssertionError: Если данные созданного курса не соответствуют запросу.
    """
    request = CreateCourseRequestSchema(
        preview_file_id=function_file.response.file.id,
        created_by_user_id=function_user.response.user.id,
    )
    response = courses_client.create_course(request=request)
    assert_create_course_response(request=request, response=response)

    return CourseFixture(request=request, response=response)


@pytest.fixture
def function_course_with_optional_fields(
    function_course: CourseFixture, courses_client: CoursesClient
) -> CourseFixture:
    """Предоставляет курс с проверенным непустым состоянием очищаемых полей.

    Получает проверенный базовый курс и подтверждает состояние отдельным GET.
    """
    original_course = function_course.response.course
    assert_course_optional_fields_are_set(original_course)
    get_course_response = courses_client.get_course_api(course_id=original_course.id)
    assert_status_code(get_course_response.status_code, HTTPStatus.OK)
    validate_json_schema(get_course_response.json(), GetCourseResponseSchema.model_json_schema())
    get_course_response_data = GetCourseResponseSchema.model_validate_json(get_course_response.text)
    assert_course(actual=get_course_response_data.course, expected=original_course)
    return function_course
