import allure
from loguru import logger

from clients.courses.courses_schema import (
    CourseSchema,
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
    GetCoursesResponseSchema,
    UpdateCourseRequestSchema,
    UpdateCourseResponseSchema,
)
from tools.assertions.base import assert_equal, assert_lens
from tools.assertions.files import assert_file
from tools.assertions.users import assert_user


@allure.step("Check create course response")
def assert_create_course_response(request: CreateCourseRequestSchema, response: CreateCourseResponseSchema) -> None:
    """Проверяет соответствие созданного курса исходному запросу.

    Args:
        request: Данные запроса на создание курса.
        response: Ответ API с данными созданного курса.

    Raises:
        AssertionError: Если поля курса или идентификаторы вложенных
            файла превью и автора не совпадают с данными запроса.
    """
    logger.info("🔎 Check create course response")
    assert_equal(response.course.title, request.title, name="title")
    assert_equal(response.course.max_score, request.max_score, name="max_score")
    assert_equal(response.course.min_score, request.min_score, name="min_score")
    assert_equal(response.course.description, request.description, name="description")
    assert_equal(response.course.estimated_time, request.estimated_time, name="estimated_time")
    assert_equal(response.course.preview_file.id, request.preview_file_id, name="preview_file_id")
    assert_equal(response.course.created_by_user.id, request.created_by_user_id, name="created_by_user_id")


@allure.step("Check update course response")
def assert_update_course_response(request: UpdateCourseRequestSchema, response: UpdateCourseResponseSchema) -> None:
    """Проверяет соответствие обновленных полей курса запросу.

    Сравнивает только явно заданные поля, включая значения None,
    переданные для очистки необязательных полей.

    Args:
        request: Данные запроса на обновление курса.
        response: Ответ API с данными обновленного курса.

    Raises:
        AssertionError: Если хотя бы одно переданное поле не обновилось.
    """
    logger.info("🔎 Check update course response")
    for name, expected in request.model_dump(exclude_unset=True, by_alias=False).items():
        assert_equal(getattr(response.course, name), expected, name=name)


@allure.step("Check course")
def assert_course(actual: CourseSchema, expected: CourseSchema) -> None:
    """Проверяет все поля курса, включая файл превью и автора.

    Args:
        actual: Фактические данные курса из ответа API.
        expected: Ожидаемые данные курса.

    Raises:
        AssertionError: Если хотя бы одно поле курса или вложенных
            файла превью и автора не соответствует ожиданиям.
    """
    logger.info("🔎 Check course")
    assert_equal(actual.id, expected.id, name="id")
    assert_equal(actual.title, expected.title, name="title")
    assert_equal(actual.max_score, expected.max_score, name="max_score")
    assert_equal(actual.min_score, expected.min_score, name="min_score")
    assert_equal(actual.description, expected.description, name="description")
    assert_equal(actual.estimated_time, expected.estimated_time, name="estimated_time")
    assert_file(actual=actual.preview_file, expected=expected.preview_file)
    assert_user(actual=actual.created_by_user, expected=expected.created_by_user)


@allure.step("Check get courses response")
def assert_get_courses_response(
    get_courses_response: GetCoursesResponseSchema,
    create_course_responses: list[CreateCourseResponseSchema],
) -> None:
    """Проверяет список курсов по ответам на их создание.

    Args:
        get_courses_response: Ответ API на запрос списка курсов.
        create_course_responses: Ожидаемые ответы на создание курсов
            в порядке их получения в списке.

    Raises:
        AssertionError: Если количество, порядок или данные курсов
            не соответствуют ожидаемым значениям.
    """
    logger.info("🔎 Check get courses response")
    assert_lens(get_courses_response.courses, create_course_responses, name="courses")

    for index, create_course_response in enumerate(create_course_responses):
        assert_course(actual=get_courses_response.courses[index], expected=create_course_response.course)
