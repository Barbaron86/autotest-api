import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.exercises.exercises_schema import (
    CreateExerciseRequestSchema,
    CreateExerciseResponseSchema,
    GetExerciseResponseSchema,
    GetExercisesRequestSchema,
    GetExercisesResponseSchema,
    UpdateExerciseRequestSchema,
    UpdateExerciseResponseSchema,
)
from clients.private_http_builder import AuthenticationUserSchema, get_private_http_client


class ExercisesClient(ApiClient):
    """API-клиент для работы с упражнениями."""

    @allure.step("Get exercises")
    def get_exercises_api(self, query: GetExercisesRequestSchema) -> Response:
        """Выполняет запрос на получение списка упражнений.

        Args:
            query: Query-параметры для получения списка упражнений.

        Returns:
            HTTP-ответ API со списком упражнений.
        """
        return self.get("/api/v1/exercises", params=query.model_dump())

    @allure.step("Get exercises with validated response")
    def get_exercises(self, query: GetExercisesRequestSchema) -> GetExercisesResponseSchema:
        """Получает список упражнений.

        Args:
            query: Query-параметры для получения списка упражнений.

        Returns:
            Данные списка упражнений.
        """
        response = self.get_exercises_api(query=query)
        response.raise_for_status()
        return GetExercisesResponseSchema.model_validate_json(response.text)

    @allure.step("Create exercise")
    def create_exercise_api(self, request: CreateExerciseRequestSchema) -> Response:
        """Выполняет запрос на создание упражнения.

        Args:
            request: Данные для создания упражнения.

        Returns:
            HTTP-ответ API на запрос создания упражнения.
        """
        return self.post("/api/v1/exercises", json=request.model_dump())

    @allure.step("Create exercise with validated response")
    def create_exercise(self, request: CreateExerciseRequestSchema) -> CreateExerciseResponseSchema:
        """Создает упражнение.

        Args:
            request: Данные для создания упражнения.

        Returns:
            Данные созданного упражнения.
        """
        response = self.create_exercise_api(request=request)
        response.raise_for_status()
        return CreateExerciseResponseSchema.model_validate_json(response.text)

    @allure.step("Get exercise by id {exercise_id}")
    def get_exercise_api(self, exercise_id: str) -> Response:
        """Выполняет запрос на получение упражнения.

        Args:
            exercise_id: Идентификатор упражнения.

        Returns:
            HTTP-ответ API с данными упражнения.
        """
        return self.get(f"/api/v1/exercises/{exercise_id}")

    @allure.step("Get exercise by id {exercise_id} with validated response")
    def get_exercise(self, exercise_id: str) -> GetExerciseResponseSchema:
        """Получает упражнение.

        Args:
            exercise_id: Идентификатор упражнения.

        Returns:
            Данные упражнения.
        """
        response = self.get_exercise_api(exercise_id=exercise_id)
        response.raise_for_status()
        return GetExerciseResponseSchema.model_validate_json(response.text)

    @allure.step("Update exercise by id {exercise_id}")
    def update_exercise_api(self, exercise_id: str, request: UpdateExerciseRequestSchema) -> Response:
        """Выполняет запрос на обновление упражнения.

        Args:
            exercise_id: Идентификатор упражнения.
            request: Данные для обновления упражнения.

        Returns:
            HTTP-ответ API на запрос обновления упражнения.
        """
        return self.patch(f"/api/v1/exercises/{exercise_id}", json=request.model_dump(exclude_unset=True))

    @allure.step("Update exercise by id {exercise_id} with validated response")
    def update_exercise(self, exercise_id: str, request: UpdateExerciseRequestSchema) -> UpdateExerciseResponseSchema:
        """Обновляет упражнение.

        Args:
            exercise_id: Идентификатор упражнения.
            request: Данные для обновления упражнения.

        Returns:
            Данные обновленного упражнения.
        """
        response = self.update_exercise_api(exercise_id=exercise_id, request=request)
        response.raise_for_status()
        return UpdateExerciseResponseSchema.model_validate_json(response.text)

    @allure.step("Delete exercise by id {exercise_id}")
    def delete_exercise_api(self, exercise_id: str) -> Response:
        """Выполняет запрос на удаление упражнения.

        Args:
            exercise_id: Идентификатор упражнения.

        Returns:
            HTTP-ответ API на запрос удаления упражнения.
        """
        return self.delete(f"/api/v1/exercises/{exercise_id}")

    @allure.step("Delete exercise by id {exercise_id} and check status")
    def delete_exercise(self, exercise_id: str) -> None:
        """Удаляет упражнение.

        Args:
            exercise_id: Идентификатор упражнения.
        """
        response = self.delete_exercise_api(exercise_id=exercise_id)
        response.raise_for_status()


def get_exercises_client(user: AuthenticationUserSchema) -> ExercisesClient:
    """Создает авторизованный API-клиент для работы с упражнениями.

    Args:
        user: Учетные данные пользователя для аутентификации.

    Returns:
        Авторизованный экземпляр ExercisesClient.
    """
    return ExercisesClient(client=get_private_http_client(user))
