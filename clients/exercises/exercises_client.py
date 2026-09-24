from typing import TypedDict

from httpx import Response

from clients.api_client import ApiClient


class GetExercisesRequestDict(TypedDict):
    """Описание структуры запроса на получение упражнений."""

    course_id: str


class CreateExerciseRequestDict(TypedDict):
    """Описание структуры запроса на создание упражнения."""

    title: str
    description: str
    course_id: str
    max_score: int | None
    min_score: int | None
    orderIndex: int
    estimated_time: str | None
    preview_file_id: str | None


class UpdateExerciseRequestDict(TypedDict):
    """Описание структуры запроса на обновление упражнения."""

    title: str | None
    description: str | None
    max_score: int | None
    min_score: int | None
    orderIndex: int | None
    estimated_time: str | None


class ExercisesClient(ApiClient):
    """API-клиент для работы с упражнениями."""

    def get_exercises_api(self, query: GetExercisesRequestDict) -> Response:
        """Получает список упражнений для курса.

        Args:
            query: Query-параметры с идентификатором курса.

        Returns:
            HTTP-ответ API со списком упражнений.
        """
        return self.get("/api/v1/exercises", params=query)

    def create_exercise_api(self, request: CreateExerciseRequestDict) -> Response:
        """Создает новое упражнение.

        Args:
            request: Данные для создания упражнения.

        Returns:
            HTTP-ответ API на запрос создания упражнения.
        """
        return self.post("/api/v1/exercises", json=request)

    def get_exercise_api(self, exercise_id: str) -> Response:
        """Получает упражнение по его идентификатору.

        Args:
            exercise_id: Идентификатор упражнения.

        Returns:
            HTTP-ответ API с данными упражнения.
        """
        return self.get(f"/api/v1/exercises/{exercise_id}")

    def update_exercise_api(self, exercise_id: str, request: UpdateExerciseRequestDict) -> Response:
        """Обновляет существующее упражнение.

        Args:
            exercise_id: Идентификатор упражнения.
            request: Данные для обновления упражнения.

        Returns:
            HTTP-ответ API на запрос обновления упражнения.
        """
        return self.patch(f"/api/v1/exercises/{exercise_id}", json=request)

    def delete_exercise_api(self, exercise_id: str) -> Response:
        """Удаляет упражнение по его идентификатору.

        Args:
            exercise_id: Идентификатор упражнения.

        Returns:
            HTTP-ответ API на запрос удаления упражнения.
        """
        return self.delete(f"/api/v1/exercises/{exercise_id}")
