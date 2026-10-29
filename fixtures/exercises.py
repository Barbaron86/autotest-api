from collections.abc import Iterator
from http import HTTPStatus

import pytest
from pydantic import BaseModel

from clients.exercises.exercises_client import ExercisesClient, get_exercises_client
from clients.exercises.exercises_schema import (
    CreateExerciseRequestSchema,
    CreateExerciseResponseSchema,
    GetExerciseResponseSchema,
)
from fixtures.courses import CourseFixture
from fixtures.users import UserFixture
from tools.assertions.base import assert_status_code
from tools.assertions.exercises import assert_create_exercise_response, assert_get_exercise_response
from tools.assertions.schema import validate_json_schema


class ExerciseFixture(BaseModel):
    """Данные задания, созданного фикстурой.

    Attributes:
        request: Запрос на создание задания.
        response: Ответ API с данными созданного задания.
    """

    request: CreateExerciseRequestSchema
    response: CreateExerciseResponseSchema


@pytest.fixture
def exercises_client(function_user: UserFixture) -> Iterator[ExercisesClient]:
    """Создает авторизованный клиент заданий для одного теста.

    Использует учетные данные созданного пользователя и закрывает
    HTTP-соединения при завершении фикстуры.

    Args:
        function_user: Фикстура с данными созданного пользователя.

    Yields:
        API-клиент для работы с заданиями.
    """
    exercises_client = get_exercises_client(user=function_user.authentication_user)

    with exercises_client.client:
        yield exercises_client


@pytest.fixture
def function_exercise(exercises_client: ExercisesClient, function_course: CourseFixture) -> ExerciseFixture:
    """Создает новое задание для курса из фикстуры.

    Args:
        exercises_client: Фикстура авторизованного API-клиента заданий.
        function_course: Фикстура с данными созданного курса.

    Returns:
        Запрос и ответ создания задания, проверенный по полям запроса.

    Raises:
        AssertionError: Если данные созданного задания не соответствуют запросу.
    """
    request = CreateExerciseRequestSchema(course_id=function_course.response.course.id)
    response = exercises_client.create_exercise(request=request)
    assert_create_exercise_response(request=request, response=response)

    return ExerciseFixture(request=request, response=response)


@pytest.fixture
def function_exercise_with_nonzero_order_index(
    exercises_client: ExercisesClient, function_course: CourseFixture
) -> ExerciseFixture:
    """Создает задание и подтверждает ненулевой индекс отдельным GET.

    Args:
        exercises_client: Фикстура авторизованного API-клиента заданий.
        function_course: Фикстура с данными курса для нового задания.

    Returns:
        Запрос и ответ создания задания с индексом 7.

    Raises:
        AssertionError: Если статус, JSON Schema или исходные данные
            созданного задания не соответствуют запросу.
    """
    request = CreateExerciseRequestSchema(course_id=function_course.response.course.id, order_index=7)
    response = exercises_client.create_exercise_api(request=request)

    assert_status_code(response.status_code, HTTPStatus.OK)
    validate_json_schema(response.json(), CreateExerciseResponseSchema.model_json_schema())
    response_data = CreateExerciseResponseSchema.model_validate_json(response.text)
    assert_create_exercise_response(request=request, response=response_data)

    get_response = exercises_client.get_exercise_api(exercise_id=response_data.exercise.id)
    assert_status_code(get_response.status_code, HTTPStatus.OK)
    validate_json_schema(get_response.json(), GetExerciseResponseSchema.model_json_schema())
    get_response_data = GetExerciseResponseSchema.model_validate_json(get_response.text)
    assert_get_exercise_response(get_exercise_response=get_response_data, create_exercise_response=response_data)

    return ExerciseFixture(request=request, response=response_data)
