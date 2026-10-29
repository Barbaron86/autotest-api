from http import HTTPStatus

import allure
import pytest
from allure_commons.types import Severity

from clients.error_schema import InternalErrorResponseSchema, ValidationErrorResponseSchema
from clients.exercises.exercises_client import ExercisesClient
from clients.exercises.exercises_schema import (
    CreateExerciseRequestSchema,
    CreateExerciseResponseSchema,
    GetExerciseResponseSchema,
    GetExercisesRequestSchema,
    GetExercisesResponseSchema,
    UpdateExerciseRequestSchema,
    UpdateExerciseResponseSchema,
)
from fixtures.courses import CourseFixture
from fixtures.exercises import ExerciseFixture
from tools.allure.epics import AllureEpic
from tools.allure.features import AllureFeature
from tools.allure.stories import AllureStory
from tools.allure.tags import AllureTag
from tools.assertions.base import assert_equal, assert_status_code
from tools.assertions.exercises import (
    assert_create_exercise_response,
    assert_exercise,
    assert_exercise_not_found_response,
    assert_exercise_with_order_index,
    assert_get_exercise_response,
    assert_get_exercises_response,
    assert_update_exercise_response,
    assert_update_exercise_with_invalid_score_range_response,
)
from tools.assertions.schema import validate_json_schema
from tools.fakers import fake


@pytest.mark.exercises
@pytest.mark.regression
@allure.tag(AllureTag.EXERCISES, AllureTag.REGRESSION)
@allure.epic(AllureEpic.LMS)
@allure.feature(AllureFeature.EXERCISES)
@allure.parent_suite(AllureEpic.LMS)
@allure.suite(AllureFeature.EXERCISES)
class TestExercises:
    """Регрессионные тесты API для работы с заданиями."""

    @allure.tag(AllureTag.CREATE_ENTITY)
    @allure.story(AllureStory.CREATE_ENTITY)
    @allure.sub_suite(AllureStory.CREATE_ENTITY)
    @allure.title("Create exercise")
    @allure.severity(Severity.BLOCKER)
    def test_create_exercise(self, exercises_client: ExercisesClient, function_course: CourseFixture) -> None:
        """Проверяет создание задания для курса из фикстуры.

        Args:
            exercises_client: Фикстура авторизованного API-клиента заданий.
            function_course: Фикстура с данными созданного курса.

        Raises:
            AssertionError: Если HTTP-статус или поля созданного задания
                не соответствуют ожидаемым значениям.
        """
        create_exercise_request = CreateExerciseRequestSchema(course_id=function_course.response.course.id)
        create_exercise_response = exercises_client.create_exercise_api(request=create_exercise_request)

        assert_status_code(create_exercise_response.status_code, HTTPStatus.OK)
        create_exercise_response_data = CreateExerciseResponseSchema.model_validate_json(create_exercise_response.text)

        assert_create_exercise_response(request=create_exercise_request, response=create_exercise_response_data)
        validate_json_schema(create_exercise_response.json(), CreateExerciseResponseSchema.model_json_schema())

    @allure.tag(AllureTag.GET_ENTITY)
    @allure.story(AllureStory.GET_ENTITY)
    @allure.sub_suite(AllureStory.GET_ENTITY)
    @allure.title("Get exercise")
    @allure.severity(Severity.BLOCKER)
    def test_get_exercise(self, exercises_client: ExercisesClient, function_exercise: ExerciseFixture) -> None:
        """Проверяет получение ранее созданного задания по идентификатору.

        Args:
            exercises_client: Фикстура авторизованного API-клиента заданий.
            function_exercise: Фикстура с данными созданного задания.

        Raises:
            AssertionError: Если HTTP-статус или данные полученного задания
                не соответствуют данным при его создании.
        """
        get_exercise_response = exercises_client.get_exercise_api(exercise_id=function_exercise.response.exercise.id)

        assert_status_code(get_exercise_response.status_code, HTTPStatus.OK)
        get_exercise_response_data = GetExerciseResponseSchema.model_validate_json(get_exercise_response.text)

        assert_get_exercise_response(
            get_exercise_response=get_exercise_response_data,
            create_exercise_response=function_exercise.response,
        )
        validate_json_schema(get_exercise_response.json(), GetExerciseResponseSchema.model_json_schema())

    @allure.tag(AllureTag.UPDATE_ENTITY)
    @allure.story(AllureStory.UPDATE_ENTITY)
    @allure.sub_suite(AllureStory.UPDATE_ENTITY)
    @allure.title("Update exercise")
    @allure.severity(Severity.CRITICAL)
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
        update_exercise_request = UpdateExerciseRequestSchema(
            title=f"{original_exercise.title[:230]} (обновлено)",
            description=f"{original_exercise.description}\nОбновленное описание.",
            max_score=(original_exercise.max_score or 0) + 1,
            min_score=(original_exercise.min_score or 0) + 1,
            order_index=original_exercise.order_index + 1,
            estimated_time=f"{original_exercise.estimated_time} (обновлено)",
        )
        update_exercise_response = exercises_client.update_exercise_api(
            exercise_id=original_exercise.id, request=update_exercise_request
        )

        assert_status_code(update_exercise_response.status_code, HTTPStatus.OK)
        update_exercise_response_data = GetExerciseResponseSchema.model_validate_json(update_exercise_response.text)

        assert_update_exercise_response(request=update_exercise_request, response=update_exercise_response_data)
        assert_equal(update_exercise_response_data.exercise.id, original_exercise.id, name="id")
        assert_equal(update_exercise_response_data.exercise.course_id, original_exercise.course_id, name="course_id")
        validate_json_schema(update_exercise_response.json(), GetExerciseResponseSchema.model_json_schema())

    @allure.tag(AllureTag.UPDATE_ENTITY)
    @allure.story(AllureStory.UPDATE_ENTITY)
    @allure.sub_suite(AllureStory.UPDATE_ENTITY)
    @allure.title("Update exercise with zero order index")
    @allure.severity(Severity.CRITICAL)
    def test_update_exercise_with_zero_order_index(
        self,
        exercises_client: ExercisesClient,
        function_exercise_with_nonzero_order_index: ExerciseFixture,
    ) -> None:
        """Проверяет сохранение целочисленного нуля в orderIndex задания.

        Использует задание с проверенным ненулевым индексом из фикстуры.
        Проверяет, что частичный PATCH меняет только индекс,
        а повторный GET подтверждает результат.

        Args:
            exercises_client: Фикстура авторизованного API-клиента заданий.
            function_exercise_with_nonzero_order_index: Фикстура с исходными
                данными задания, имеющего ненулевой индекс.

        Raises:
            AssertionError: Если индекс не изменился на целочисленный ноль
                или изменились остальные данные задания после PATCH либо GET.
        """
        original_exercise = function_exercise_with_nonzero_order_index.response.exercise
        new_order_index = 0
        update_exercise_request = UpdateExerciseRequestSchema(order_index=new_order_index)

        update_exercise_response = exercises_client.update_exercise_api(
            exercise_id=original_exercise.id, request=update_exercise_request
        )

        assert_status_code(update_exercise_response.status_code, HTTPStatus.OK)
        update_exercise_response_json = update_exercise_response.json()
        validate_json_schema(update_exercise_response_json, UpdateExerciseResponseSchema.model_json_schema())
        assert_exercise_with_order_index(
            actual=update_exercise_response_json, original_exercise=original_exercise, order_index=new_order_index
        )

        get_exercise_response = exercises_client.get_exercise_api(exercise_id=original_exercise.id)

        assert_status_code(get_exercise_response.status_code, HTTPStatus.OK)
        get_exercise_response_json = get_exercise_response.json()
        validate_json_schema(get_exercise_response_json, GetExerciseResponseSchema.model_json_schema())
        assert_exercise_with_order_index(
            actual=get_exercise_response_json, original_exercise=original_exercise, order_index=new_order_index
        )

    @allure.tag(AllureTag.VALIDATE_ENTITY)
    @allure.story(AllureStory.VALIDATE_ENTITY)
    @allure.sub_suite(AllureStory.VALIDATE_ENTITY)
    @allure.title("Update exercise with invalid score range")
    @allure.severity(Severity.NORMAL)
    def test_update_exercise_with_invalid_score_range(
        self, exercises_client: ExercisesClient, function_exercise: ExerciseFixture
    ) -> None:
        """Проверяет отказ в обновлении задания при maxScore меньше minScore.

        Args:
            exercises_client: Фикстура авторизованного API-клиента заданий.
            function_exercise: Фикстура с исходными данными созданного задания.

        Raises:
            AssertionError: Если ошибка валидации не соответствует контракту
                или отклоненный PATCH изменил сохраненные данные задания.
        """
        original_exercise = function_exercise.response.exercise
        invalid_max_score, invalid_min_score = fake.invalid_score_range()
        update_exercise_request = UpdateExerciseRequestSchema(max_score=invalid_max_score, min_score=invalid_min_score)

        update_exercise_response = exercises_client.update_exercise_api(
            exercise_id=original_exercise.id, request=update_exercise_request
        )

        assert_status_code(update_exercise_response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        validate_json_schema(update_exercise_response.json(), ValidationErrorResponseSchema.model_json_schema())
        update_exercise_response_data = ValidationErrorResponseSchema.model_validate_json(update_exercise_response.text)

        assert_update_exercise_with_invalid_score_range_response(
            actual=update_exercise_response_data, request=update_exercise_request
        )

        get_exercise_response = exercises_client.get_exercise_api(exercise_id=original_exercise.id)

        assert_status_code(get_exercise_response.status_code, HTTPStatus.OK)
        validate_json_schema(get_exercise_response.json(), GetExerciseResponseSchema.model_json_schema())
        get_exercise_response_data = GetExerciseResponseSchema.model_validate_json(get_exercise_response.text)

        assert_exercise(actual=get_exercise_response_data.exercise, expected=original_exercise)

    @allure.tag(AllureTag.DELETE_ENTITY)
    @allure.story(AllureStory.DELETE_ENTITY)
    @allure.sub_suite(AllureStory.DELETE_ENTITY)
    @allure.title("Delete exercise")
    @allure.severity(Severity.CRITICAL)
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
        delete_exercise_response = exercises_client.delete_exercise_api(exercise_id=exercise_id)

        assert_status_code(delete_exercise_response.status_code, HTTPStatus.OK)

        get_exercise_response = exercises_client.get_exercise_api(exercise_id=exercise_id)

        assert_status_code(get_exercise_response.status_code, HTTPStatus.NOT_FOUND)
        get_exercise_response_data = InternalErrorResponseSchema.model_validate_json(get_exercise_response.text)

        assert_exercise_not_found_response(actual=get_exercise_response_data)
        validate_json_schema(get_exercise_response.json(), InternalErrorResponseSchema.model_json_schema())

    @allure.tag(AllureTag.GET_ENTITIES)
    @allure.story(AllureStory.GET_ENTITIES)
    @allure.sub_suite(AllureStory.GET_ENTITIES)
    @allure.title("Get exercises")
    @allure.severity(Severity.BLOCKER)
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
        get_exercises_query = GetExercisesRequestSchema(course_id=function_course.response.course.id)
        get_exercises_response = exercises_client.get_exercises_api(query=get_exercises_query)

        assert_status_code(get_exercises_response.status_code, HTTPStatus.OK)
        get_exercises_response_data = GetExercisesResponseSchema.model_validate_json(get_exercises_response.text)

        assert_get_exercises_response(
            get_exercises_response=get_exercises_response_data,
            create_exercise_responses=[function_exercise.response],
        )
        validate_json_schema(get_exercises_response.json(), GetExercisesResponseSchema.model_json_schema())
