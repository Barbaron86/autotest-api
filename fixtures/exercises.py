from collections.abc import Iterator

import pytest
from pydantic import BaseModel

from clients.exercises.exercises_client import ExercisesClient, get_exercises_client
from clients.exercises.exercises_schema import CreateExerciseRequestSchema, CreateExerciseResponseSchema
from fixtures.courses import CourseFixture
from fixtures.users import UserFixture


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
        Данные запроса на создание задания и ответа API.
    """
    request = CreateExerciseRequestSchema(course_id=function_course.response.course.id)
    response = exercises_client.create_exercise(request=request)

    return ExerciseFixture(request=request, response=response)
