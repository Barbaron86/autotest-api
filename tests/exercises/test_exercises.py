from http import HTTPStatus

import pytest

from clients.error_schema import InternalErrorResponseSchema
from clients.exercises.exercises_client import ExercisesClient
from clients.exercises.exercises_schema import (
    CreateExerciseRequestSchema,
    CreateExerciseResponseSchema,
    GetExerciseResponseSchema,
    GetExercisesRequestSchema,
    GetExercisesResponseSchema,
    UpdateExerciseRequestSchema,
)
from fixtures.courses import CourseFixture
from fixtures.exercises import ExerciseFixture
from tools.assertions.base import assert_equal, assert_status_code
from tools.assertions.exercises import (
    assert_create_exercise_response,
    assert_exercise_not_found_response,
    assert_get_exercise_response,
    assert_get_exercises_response,
    assert_update_exercise_response,
)
from tools.assertions.schema import validate_json_schema


@pytest.mark.exercises
@pytest.mark.regression
class TestExercises:
    """Регрессионные тесты API для работы с заданиями."""

    def test_create_exercise(self, exercises_client: ExercisesClient, function_course: CourseFixture) -> None:
        """Проверяет создание задания для курса из фикстуры.

        Args:
            exercises_client: Фикстура авторизованного API-клиента заданий.
            function_course: Фикстура с данными созданного курса.

        Raises:
            AssertionError: Если HTTP-статус или поля созданного задания
                не соответствуют ожидаемым значениям.
        """
        request = CreateExerciseRequestSchema(course_id=function_course.response.course.id)
        response = exercises_client.create_exercise_api(request=request)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = CreateExerciseResponseSchema.model_validate_json(response.text)

        assert_create_exercise_response(request=request, response=response_data)
        validate_json_schema(response.json(), CreateExerciseResponseSchema.model_json_schema())

    def test_get_exercise(self, exercises_client: ExercisesClient, function_exercise: ExerciseFixture) -> None:
        """Проверяет получение ранее созданного задания по идентификатору.

        Args:
            exercises_client: Фикстура авторизованного API-клиента заданий.
            function_exercise: Фикстура с данными созданного задания.

        Raises:
            AssertionError: Если HTTP-статус или данные полученного задания
                не соответствуют данным при его создании.
        """
        response = exercises_client.get_exercise_api(exercise_id=function_exercise.response.exercise.id)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = GetExerciseResponseSchema.model_validate_json(response.text)

        assert_get_exercise_response(
            get_exercise_response=response_data,
            create_exercise_response=function_exercise.response,
        )
        validate_json_schema(response.json(), GetExerciseResponseSchema.model_json_schema())

    def test_update_exercise(self, exercises_client: ExercisesClient, function_exercise: ExerciseFixture) -> None:
        """Проверяет обновление всех редактируемых полей задания.

        Задает отличающиеся от исходных значения и проверяет сохранение
        идентификатора задания и его связи с курсом.

        Args:
            exercises_client: Фикстура авторизованного API-клиента заданий.
            function_exercise: Фикстура с данными созданного задания.

        Raises:
            AssertionError: Если HTTP-статус, обновленные поля или
                неизменяемые данные задания не соответствуют ожиданиям.
        """
        original_exercise = function_exercise.response.exercise
        request = UpdateExerciseRequestSchema(
            title=f"{original_exercise.title[:230]} (обновлено)",
            description=f"{original_exercise.description}\nОбновленное описание.",
            max_score=(original_exercise.max_score or 0) + 1,
            min_score=(original_exercise.min_score or 0) + 1,
            order_index=original_exercise.order_index + 1,
            estimated_time=f"{original_exercise.estimated_time} (обновлено)",
        )
        response = exercises_client.update_exercise_api(exercise_id=original_exercise.id, request=request)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = GetExerciseResponseSchema.model_validate_json(response.text)

        assert_update_exercise_response(request=request, response=response_data)
        assert_equal(response_data.exercise.id, original_exercise.id, name="id")
        assert_equal(response_data.exercise.course_id, original_exercise.course_id, name="course_id")
        validate_json_schema(response.json(), GetExerciseResponseSchema.model_json_schema())

    def test_delete_exercise(self, exercises_client: ExercisesClient, function_exercise: ExerciseFixture) -> None:
        """Проверяет удаление задания и его отсутствие при повторном запросе.

        Args:
            exercises_client: Фикстура авторизованного API-клиента заданий.
            function_exercise: Фикстура с данными созданного задания.

        Raises:
            AssertionError: Если HTTP-статусы или сообщение об отсутствии
                удаленного задания не соответствуют ожиданиям.
        """
        exercise_id = function_exercise.response.exercise.id
        delete_response = exercises_client.delete_exercise_api(exercise_id=exercise_id)

        assert_status_code(delete_response.status_code, HTTPStatus.OK)

        get_response = exercises_client.get_exercise_api(exercise_id=exercise_id)

        assert_status_code(get_response.status_code, HTTPStatus.NOT_FOUND)
        response_data = InternalErrorResponseSchema.model_validate_json(get_response.text)

        assert_exercise_not_found_response(actual=response_data)
        validate_json_schema(get_response.json(), InternalErrorResponseSchema.model_json_schema())

    def test_get_exercises(
        self,
        exercises_client: ExercisesClient,
        function_course: CourseFixture,
        function_exercise: ExerciseFixture,
    ) -> None:
        """Проверяет список заданий, относящихся к указанному курсу.

        Args:
            exercises_client: Фикстура авторизованного API-клиента заданий.
            function_course: Фикстура с данными созданного курса.
            function_exercise: Фикстура с данными созданного задания.

        Raises:
            AssertionError: Если HTTP-статус, количество или данные
                полученных заданий не соответствуют ожиданиям.
        """
        query = GetExercisesRequestSchema(course_id=function_course.response.course.id)
        response = exercises_client.get_exercises_api(query=query)

        assert_status_code(response.status_code, HTTPStatus.OK)
        response_data = GetExercisesResponseSchema.model_validate_json(response.text)

        assert_get_exercises_response(
            get_exercises_response=response_data,
            create_exercise_responses=[function_exercise.response],
        )
        validate_json_schema(response.json(), GetExercisesResponseSchema.model_json_schema())
