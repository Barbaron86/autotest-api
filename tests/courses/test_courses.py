from http import HTTPStatus

import allure
import pytest
from allure_commons.types import Severity

from clients.courses.courses_client import CoursesClient
from clients.courses.courses_schema import (
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
    GetCourseResponseSchema,
    GetCoursesQuerySchema,
    GetCoursesResponseSchema,
    UpdateCourseRequestSchema,
    UpdateCourseResponseSchema,
)
from clients.error_schema import InternalErrorResponseSchema, ValidationErrorResponseSchema
from fixtures.courses import CourseFixture
from fixtures.files import FileFixture
from fixtures.users import UserFixture
from tools.allure.epics import AllureEpic
from tools.allure.features import AllureFeature
from tools.allure.stories import AllureStory
from tools.allure.tags import AllureTag
from tools.assertions.base import assert_equal, assert_status_code
from tools.assertions.courses import (
    assert_course,
    assert_course_with_cleared_optional_fields,
    assert_create_course_response,
    assert_get_courses_response,
    assert_update_course_response,
    assert_update_course_with_invalid_score_range_response,
)
from tools.assertions.errors import (
    assert_internal_error_response,
)
from tools.assertions.files import assert_file
from tools.assertions.schema import validate_json_schema
from tools.assertions.users import assert_user
from tools.fakers import fake


@pytest.mark.courses
@pytest.mark.regression
@allure.tag(AllureTag.COURSES, AllureTag.REGRESSION)
@allure.epic(AllureEpic.LMS)
@allure.feature(AllureFeature.COURSES)
@allure.parent_suite(AllureEpic.LMS)
@allure.suite(AllureFeature.COURSES)
class TestCourses:
    """Регрессионные тесты API для работы с курсами."""

    @allure.tag(AllureTag.CREATE_ENTITY)
    @allure.story(AllureStory.CREATE_ENTITY)
    @allure.sub_suite(AllureStory.CREATE_ENTITY)
    @allure.title("Create course")
    @allure.severity(Severity.BLOCKER)
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
        create_course_request = CreateCourseRequestSchema(
            preview_file_id=function_file.response.file.id,
            created_by_user_id=function_user.response.user.id,
        )
        create_course_response = courses_client.create_course_api(request=create_course_request)

        assert_status_code(create_course_response.status_code, HTTPStatus.OK)
        create_course_response_data = CreateCourseResponseSchema.model_validate_json(create_course_response.text)

        assert_create_course_response(request=create_course_request, response=create_course_response_data)
        assert_file(actual=create_course_response_data.course.preview_file, expected=function_file.response.file)
        assert_user(actual=create_course_response_data.course.created_by_user, expected=function_user.response.user)
        validate_json_schema(create_course_response.json(), CreateCourseResponseSchema.model_json_schema())

    @allure.tag(AllureTag.UPDATE_ENTITY)
    @allure.story(AllureStory.UPDATE_ENTITY)
    @allure.sub_suite(AllureStory.UPDATE_ENTITY)
    @allure.title("Update course")
    @allure.severity(Severity.CRITICAL)
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
        update_course_request = UpdateCourseRequestSchema(
            title=f"{original_course.title[:230]} (обновлено)",
            max_score=(original_course.max_score or 0) + 1,
            min_score=(original_course.min_score or 0) + 1,
            description=f"{original_course.description}\nОбновленное описание.",
            estimated_time=f"{original_course.estimated_time} (обновлено)",
        )
        update_course_response = courses_client.update_course_api(
            course_id=original_course.id, request=update_course_request
        )

        assert_status_code(update_course_response.status_code, HTTPStatus.OK)
        update_course_response_data = UpdateCourseResponseSchema.model_validate_json(update_course_response.text)

        assert_update_course_response(request=update_course_request, response=update_course_response_data)
        assert_equal(update_course_response_data.course.id, original_course.id, name="id")
        assert_file(actual=update_course_response_data.course.preview_file, expected=original_course.preview_file)
        assert_user(actual=update_course_response_data.course.created_by_user, expected=original_course.created_by_user)
        validate_json_schema(update_course_response.json(), UpdateCourseResponseSchema.model_json_schema())

    @allure.tag(AllureTag.UPDATE_ENTITY)
    @allure.story(AllureStory.UPDATE_ENTITY)
    @allure.sub_suite(AllureStory.UPDATE_ENTITY)
    @allure.title("Partial update course")
    @allure.severity(Severity.CRITICAL)
    def test_partial_update_course(self, courses_client: CoursesClient, function_course: CourseFixture) -> None:
        """Проверяет обновление названия без изменения остальных полей курса.

        Args:
            courses_client: Фикстура авторизованного API-клиента курсов.
            function_course: Фикстура с исходными данными созданного курса.

        Raises:
            AssertionError: Если название не обновилось или изменились
                другие поля в ответе PATCH либо при повторном GET.
        """
        original_course = function_course.response.course
        update_course_request = UpdateCourseRequestSchema(title=f"{original_course.title[:230]} (частично)")
        expected_course = original_course.model_copy(update={"title": update_course_request.title})

        update_course_response = courses_client.update_course_api(
            course_id=original_course.id, request=update_course_request
        )

        assert_status_code(update_course_response.status_code, HTTPStatus.OK)
        validate_json_schema(update_course_response.json(), UpdateCourseResponseSchema.model_json_schema())
        update_course_response_data = UpdateCourseResponseSchema.model_validate_json(update_course_response.text)

        assert_update_course_response(request=update_course_request, response=update_course_response_data)
        assert_course(actual=update_course_response_data.course, expected=expected_course)

        get_course_response = courses_client.get_course_api(course_id=original_course.id)

        assert_status_code(get_course_response.status_code, HTTPStatus.OK)
        validate_json_schema(get_course_response.json(), GetCourseResponseSchema.model_json_schema())
        get_course_response_data = GetCourseResponseSchema.model_validate_json(get_course_response.text)

        assert_course(actual=get_course_response_data.course, expected=expected_course)

    @allure.tag(AllureTag.UPDATE_ENTITY)
    @allure.story(AllureStory.UPDATE_ENTITY)
    @allure.sub_suite(AllureStory.UPDATE_ENTITY)
    @allure.title("Clear optional course fields")
    @allure.severity(Severity.CRITICAL)
    def test_clear_optional_course_fields(
        self, courses_client: CoursesClient, function_course_with_optional_fields: CourseFixture
    ) -> None:
        """Проверяет очистку необязательных полей курса явным null.

        Подтверждает непустое исходное состояние очищаемых полей,
        сохранение остальных данных и результат повторным GET.

        Args:
            courses_client: Фикстура авторизованного API-клиента курсов.
            function_course_with_optional_fields: Курс с проверенными непустыми полями.

        Raises:
            AssertionError: Если поля не очищены, отсутствуют в JSON
                или изменились другие данные курса после PATCH либо GET.
        """
        original_course = function_course_with_optional_fields.response.course
        update_course_request = UpdateCourseRequestSchema(max_score=None, min_score=None, estimated_time=None)

        update_course_response = courses_client.update_course_api(
            course_id=original_course.id, request=update_course_request
        )

        assert_status_code(update_course_response.status_code, HTTPStatus.OK)
        update_course_response_json = update_course_response.json()
        validate_json_schema(update_course_response_json, UpdateCourseResponseSchema.model_json_schema())
        assert_course_with_cleared_optional_fields(actual=update_course_response_json, original_course=original_course)

        get_course_response = courses_client.get_course_api(course_id=original_course.id)

        assert_status_code(get_course_response.status_code, HTTPStatus.OK)
        get_course_response_json = get_course_response.json()
        validate_json_schema(get_course_response_json, GetCourseResponseSchema.model_json_schema())
        assert_course_with_cleared_optional_fields(actual=get_course_response_json, original_course=original_course)

    @allure.tag(AllureTag.VALIDATE_ENTITY)
    @allure.story(AllureStory.VALIDATE_ENTITY)
    @allure.sub_suite(AllureStory.VALIDATE_ENTITY)
    @allure.title("Update course with invalid score range")
    @allure.severity(Severity.NORMAL)
    def test_update_course_with_invalid_score_range(
        self, courses_client: CoursesClient, function_course: CourseFixture
    ) -> None:
        """Проверяет отказ в обновлении курса при maxScore меньше minScore.

        Args:
            courses_client: Фикстура авторизованного API-клиента курсов.
            function_course: Фикстура с исходными данными созданного курса.

        Raises:
            AssertionError: Если ошибка валидации не соответствует контракту
                или отклоненный PATCH изменил сохраненные данные курса.
        """
        original_course = function_course.response.course
        invalid_max_score, invalid_min_score = fake.invalid_score_range()
        update_course_request = UpdateCourseRequestSchema(max_score=invalid_max_score, min_score=invalid_min_score)

        update_course_response = courses_client.update_course_api(
            course_id=original_course.id, request=update_course_request
        )

        assert_status_code(update_course_response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        validate_json_schema(update_course_response.json(), ValidationErrorResponseSchema.model_json_schema())
        update_course_response_data = ValidationErrorResponseSchema.model_validate_json(update_course_response.text)

        assert_update_course_with_invalid_score_range_response(
            actual=update_course_response_data, request=update_course_request
        )

        get_course_response = courses_client.get_course_api(course_id=original_course.id)

        assert_status_code(get_course_response.status_code, HTTPStatus.OK)
        validate_json_schema(get_course_response.json(), GetCourseResponseSchema.model_json_schema())
        get_course_response_data = GetCourseResponseSchema.model_validate_json(get_course_response.text)

        assert_course(actual=get_course_response_data.course, expected=original_course)

    @allure.tag(AllureTag.DELETE_ENTITY)
    @allure.story(AllureStory.DELETE_ENTITY)
    @allure.sub_suite(AllureStory.DELETE_ENTITY)
    @allure.title("Delete course")
    @allure.severity(Severity.CRITICAL)
    def test_delete_course(self, courses_client: CoursesClient, function_course: CourseFixture) -> None:
        """Проверяет удаление курса и его недоступность при повторном GET.

        Args:
            courses_client: Фикстура авторизованного API-клиента курсов.
            function_course: Фикстура с данными созданного курса.

        Raises:
            AssertionError: Если HTTP-статусы или сообщение об отсутствии
                удаленного курса не соответствуют ожиданиям.
        """
        course_id = function_course.response.course.id
        delete_course_response = courses_client.delete_course_api(course_id=course_id)

        assert_status_code(delete_course_response.status_code, HTTPStatus.OK)

        get_course_response = courses_client.get_course_api(course_id=course_id)

        assert_status_code(get_course_response.status_code, HTTPStatus.NOT_FOUND)
        validate_json_schema(get_course_response.json(), InternalErrorResponseSchema.model_json_schema())
        get_course_response_data = InternalErrorResponseSchema.model_validate_json(get_course_response.text)

        assert_internal_error_response(
            actual=get_course_response_data,
            expected=InternalErrorResponseSchema(detail="Course not found"),
        )

    @allure.tag(AllureTag.GET_ENTITY)
    @allure.story(AllureStory.GET_ENTITY)
    @allure.sub_suite(AllureStory.GET_ENTITY)
    @allure.title("Get course by id")
    @allure.severity(Severity.BLOCKER)
    def test_get_course(self, courses_client: CoursesClient, function_course: CourseFixture) -> None:
        """Проверяет получение созданного курса по идентификатору.

        Подтверждает исходное состояние курса по запросу создания,
        проверяет структуру JSON и все поля курса, включая превью и автора.

        Args:
            courses_client: Фикстура авторизованного API-клиента курсов.
            function_course: Фикстура с запросом и ответом создания курса.

        Raises:
            AssertionError: Если HTTP-статус или данные курса
                не соответствуют ожидаемым значениям.
        """
        expected_course = function_course.response.course

        get_course_response = courses_client.get_course_api(course_id=expected_course.id)

        assert_status_code(get_course_response.status_code, HTTPStatus.OK)
        validate_json_schema(get_course_response.json(), GetCourseResponseSchema.model_json_schema())
        get_course_response_data = GetCourseResponseSchema.model_validate_json(get_course_response.text)

        assert_course(actual=get_course_response_data.course, expected=expected_course)

    @allure.tag(AllureTag.GET_ENTITIES)
    @allure.story(AllureStory.GET_ENTITIES)
    @allure.sub_suite(AllureStory.GET_ENTITIES)
    @allure.title("Get courses")
    @allure.severity(Severity.BLOCKER)
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
        get_courses_query = GetCoursesQuerySchema(user_id=function_user.response.user.id)
        get_courses_response = courses_client.get_courses_api(query=get_courses_query)

        assert_status_code(get_courses_response.status_code, HTTPStatus.OK)
        get_courses_response_data = GetCoursesResponseSchema.model_validate_json(get_courses_response.text)

        assert_get_courses_response(
            get_courses_response=get_courses_response_data,
            create_course_responses=[function_course.response],
        )
        validate_json_schema(get_courses_response.json(), GetCoursesResponseSchema.model_json_schema())
