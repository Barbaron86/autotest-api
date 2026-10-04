from collections.abc import Iterator

import pytest
from pydantic import BaseModel

from clients.courses.courses_client import CoursesClient, get_courses_client
from clients.courses.courses_schema import CreateCourseRequestSchema, CreateCourseResponseSchema
from fixtures.files import FileFixture
from fixtures.users import UserFixture


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
        Данные запроса на создание курса и ответа API.
    """
    request = CreateCourseRequestSchema(
        preview_file_id=function_file.response.file.id,
        created_by_user_id=function_user.response.user.id,
    )
    response = courses_client.create_course(request=request)

    return CourseFixture(request=request, response=response)
