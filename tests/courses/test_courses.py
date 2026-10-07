from http import HTTPStatus

import pytest

from clients.courses.courses_client import CoursesClient
from clients.courses.courses_schema import (
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
    GetCoursesQuerySchema,
    GetCoursesResponseSchema,
    UpdateCourseRequestSchema,
    UpdateCourseResponseSchema,
)
from fixtures.courses import CourseFixture
from fixtures.files import FileFixture
from fixtures.users import UserFixture
from tools.assertions.base import assert_equal, assert_status_code
from tools.assertions.courses import (
    assert_create_course_response,
    assert_get_courses_response,
    assert_update_course_response,
)
from tools.assertions.files import assert_file
from tools.assertions.schema import validate_json_schema
from tools.assertions.users import assert_user


@pytest.mark.courses
@pytest.mark.regression
class TestCourses:
    """Регрессионные тесты API для работы с курсами."""

    def test_create_course(
        self,
        courses_client: CoursesClient,
        function_file: FileFixture,
        function_user: UserFixture,
    ) -> None:
        """Проверяет создание курса с файлом и пользователем из фикстур.

        Args:
            courses_client: Фикстура авторизованного API-клиента курсов.
            function_file: Фикстура с данными загруженного файла превью.
            function_user: Фикстура с данными автора курса.

        Raises:
            AssertionError: Если HTTP-статус или данные созданного курса
                не соответствуют ожидаемым значениям.
        """
        request = CreateCourseRequestSchema(
            preview_file_id=function_file.response.file.id,
            created_by_user_id=function_user.response.user.id,
        )
        response = courses_client.create_course_api(request=request)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = CreateCourseResponseSchema.model_validate_json(response.text)

        assert_create_course_response(request=request, response=response_data)
        assert_file(actual=response_data.course.preview_file, expected=function_file.response.file)
        assert_user(actual=response_data.course.created_by_user, expected=function_user.response.user)
        validate_json_schema(response.json(), CreateCourseResponseSchema.model_json_schema())

    def test_update_course(self, courses_client: CoursesClient, function_course: CourseFixture) -> None:
        """Проверяет обновление всех редактируемых полей курса.

        Дополнительно проверяет сохранение идентификатора курса,
        файла превью и данных автора после обновления.

        Args:
            courses_client: Фикстура авторизованного API-клиента курсов.
            function_course: Фикстура с данными созданного курса.

        Raises:
            AssertionError: Если HTTP-статус, обновленные поля или
                неизменяемые данные курса не соответствуют ожиданиям.
        """
        original_course = function_course.response.course
        request = UpdateCourseRequestSchema(
            title=f"{original_course.title[:230]} (обновлено)",
            max_score=(original_course.max_score or 0) + 1,
            min_score=(original_course.min_score or 0) + 1,
            description=f"{original_course.description}\nОбновленное описание.",
            estimated_time=f"{original_course.estimated_time} (обновлено)",
        )
        response = courses_client.update_course_api(course_id=original_course.id, request=request)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = UpdateCourseResponseSchema.model_validate_json(response.text)

        assert_update_course_response(request=request, response=response_data)
        assert_equal(response_data.course.id, original_course.id, name="id")
        assert_file(actual=response_data.course.preview_file, expected=original_course.preview_file)
        assert_user(actual=response_data.course.created_by_user, expected=original_course.created_by_user)
        validate_json_schema(response.json(), UpdateCourseResponseSchema.model_json_schema())

    def test_get_courses(
        self,
        courses_client: CoursesClient,
        function_user: UserFixture,
        function_course: CourseFixture,
    ) -> None:
        """Проверяет список курсов, созданных указанным пользователем.

        Сравнивает количество курсов и все их поля, включая
        вложенные данные файла превью и автора.

        Args:
            courses_client: Фикстура авторизованного API-клиента курсов.
            function_user: Фикстура с данными автора курса.
            function_course: Фикстура с данными созданного курса.

        Raises:
            AssertionError: Если HTTP-статус, количество или данные
                полученных курсов не соответствуют ожиданиям.
        """
        query = GetCoursesQuerySchema(user_id=function_user.response.user.id)
        response = courses_client.get_courses_api(query=query)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = GetCoursesResponseSchema.model_validate_json(response.text)

        assert_get_courses_response(
            get_courses_response=response_data,
            create_course_responses=[function_course.response],
        )
        validate_json_schema(response.json(), GetCoursesResponseSchema.model_json_schema())
