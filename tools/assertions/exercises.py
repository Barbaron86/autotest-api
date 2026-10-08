import allure

from clients.error_schema import InternalErrorResponseSchema
from clients.exercises.exercises_schema import (
    CreateExerciseRequestSchema,
    CreateExerciseResponseSchema,
    ExerciseSchema,
    GetExerciseResponseSchema,
    GetExercisesResponseSchema,
    UpdateExerciseRequestSchema,
    UpdateExerciseResponseSchema,
)
from tools.assertions.base import assert_equal, assert_lens
from tools.assertions.errors import assert_internal_error_response


@allure.step("Check create exercise response")
def assert_create_exercise_response(
    request: CreateExerciseRequestSchema, response: CreateExerciseResponseSchema
) -> None:
    """Проверяет соответствие созданного задания исходному запросу.

    Args:
        request: Данные запроса на создание задания.
        response: Ответ API с данными созданного задания.

    Raises:
        AssertionError: Если хотя бы одно поле задания не совпадает
            с данными запроса.
    """
    assert_equal(response.exercise.title, request.title, name="title")
    assert_equal(response.exercise.description, request.description, name="description")
    assert_equal(response.exercise.course_id, request.course_id, name="course_id")
    assert_equal(response.exercise.max_score, request.max_score, name="max_score")
    assert_equal(response.exercise.min_score, request.min_score, name="min_score")
    assert_equal(response.exercise.order_index, request.order_index, name="order_index")
    assert_equal(response.exercise.estimated_time, request.estimated_time, name="estimated_time")


@allure.step("Check exercise")
def assert_exercise(actual: ExerciseSchema, expected: ExerciseSchema) -> None:
    """Проверяет совпадение всех полей задания.

    Args:
        actual: Фактические данные задания из ответа API.
        expected: Ожидаемые данные задания.

    Raises:
        AssertionError: Если хотя бы одно поле задания не совпадает.
    """
    assert_equal(actual.id, expected.id, name="id")
    assert_equal(actual.title, expected.title, name="title")
    assert_equal(actual.description, expected.description, name="description")
    assert_equal(actual.course_id, expected.course_id, name="course_id")
    assert_equal(actual.max_score, expected.max_score, name="max_score")
    assert_equal(actual.min_score, expected.min_score, name="min_score")
    assert_equal(actual.order_index, expected.order_index, name="order_index")
    assert_equal(actual.estimated_time, expected.estimated_time, name="estimated_time")


@allure.step("Check get exercise response")
def assert_get_exercise_response(
    get_exercise_response: GetExerciseResponseSchema,
    create_exercise_response: CreateExerciseResponseSchema,
) -> None:
    """Проверяет полученное задание по данным его создания.

    Args:
        get_exercise_response: Ответ API на запрос получения задания.
        create_exercise_response: Ответ API на запрос создания задания.

    Raises:
        AssertionError: Если данные полученного задания не совпадают
            с данными созданного задания.
    """
    assert_exercise(actual=get_exercise_response.exercise, expected=create_exercise_response.exercise)


@allure.step("Check update exercise response")
def assert_update_exercise_response(
    request: UpdateExerciseRequestSchema,
    response: GetExerciseResponseSchema | UpdateExerciseResponseSchema,
) -> None:
    """Проверяет соответствие обновленных полей задания запросу.

    Сравнивает только явно заданные поля, включая значения None,
    переданные для очистки необязательных полей.

    Args:
        request: Данные запроса на обновление задания.
        response: Ответ API с данными обновленного задания.

    Raises:
        AssertionError: Если хотя бы одно переданное поле не обновилось.
    """
    for name, expected in request.model_dump(exclude_unset=True, by_alias=False).items():
        assert_equal(getattr(response.exercise, name), expected, name=name)


@allure.step("Check exercise not found response")
def assert_exercise_not_found_response(actual: InternalErrorResponseSchema) -> None:
    """Проверяет сообщение API об отсутствии задания.

    Args:
        actual: Фактический ответ API с сообщением об ошибке.

    Raises:
        AssertionError: Если ответ не содержит сообщение «Exercise not found».
    """
    expected = InternalErrorResponseSchema(detail="Exercise not found")
    assert_internal_error_response(actual=actual, expected=expected)


@allure.step("Check get exercises response")
def assert_get_exercises_response(
    get_exercises_response: GetExercisesResponseSchema,
    create_exercise_responses: list[CreateExerciseResponseSchema],
) -> None:
    """Проверяет список заданий по ответам на их создание.

    Args:
        get_exercises_response: Ответ API на запрос списка заданий.
        create_exercise_responses: Ожидаемые ответы на создание заданий
            в порядке их получения в списке.

    Raises:
        AssertionError: Если количество, порядок или данные заданий
            не соответствуют ожидаемым значениям.
    """
    assert_lens(get_exercises_response.exercises, create_exercise_responses, name="exercises")

    for index, create_exercise_response in enumerate(create_exercise_responses):
        assert_exercise(actual=get_exercises_response.exercises[index], expected=create_exercise_response.exercise)
