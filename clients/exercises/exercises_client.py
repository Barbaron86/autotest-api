from typing import TypedDict

from httpx import Response

from clients.api_client import ApiClient
from clients.private_http_builder import AuthenticationUserDict, get_private_http_client


class ExerciseDict(TypedDict):
    """Описание структуры данных упражнения."""

    id: str
    title: str
    description: str
    courseId: str
    maxScore: int | None
    minScore: int | None
    orderIndex: int
    estimatedTime: str | None


class GetExerciseResponseDict(TypedDict):
    """Описание структуры ответа на запрос получения упражнения."""

    exercise: ExerciseDict


class GetExercisesResponseDict(TypedDict):
    """Описание структуры ответа на запрос получения списка упражнений."""

    exercises: list[ExerciseDict]


class GetExercisesRequestDict(TypedDict):
    """Описание структуры запроса на получение упражнений."""

    course_id: str


class CreateExerciseRequestDict(TypedDict):
    """Описание структуры запроса на создание упражнения."""

    title: str
    description: str
    courseId: str
    maxScore: int | None
    minScore: int | None
    orderIndex: int
    estimatedTime: str | None


class CreateExerciseResponseDict(TypedDict):
    """Описание структуры ответа на запрос создания упражнения."""

    exercise: ExerciseDict


class UpdateExerciseRequestDict(TypedDict):
    """Описание структуры запроса на обновление упражнения."""

    title: str | None
    description: str | None
    maxScore: int | None
    minScore: int | None
    orderIndex: int | None
    estimatedTime: str | None


class UpdateExerciseResponseDict(TypedDict):
    """Описание структуры ответа на запрос обновления упражнения."""

    exercise: ExerciseDict


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

    def get_exercises(self, query: GetExercisesRequestDict) -> GetExercisesResponseDict:
        """Получает список упражнений для курса и возвращает их данные.

        Args:
            query: Query-параметры с идентификатором курса.

        Returns:
            Данные ответа со списком упражнений.
        """
        response = self.get_exercises_api(query=query)
        response.raise_for_status()
        response_data: GetExercisesResponseDict = response.json()
        return response_data

    def create_exercise_api(self, request: CreateExerciseRequestDict) -> Response:
        """Создает новое упражнение.

        Args:
            request: Данные для создания упражнения.

        Returns:
            HTTP-ответ API на запрос создания упражнения.
        """
        return self.post("/api/v1/exercises", json=request)

    def create_exercise(self, request: CreateExerciseRequestDict) -> CreateExerciseResponseDict:
        """Создает новое упражнение и возвращает его данные.

        Args:
            request: Данные для создания упражнения.

        Returns:
            Данные созданного упражнения.
        """
        response = self.create_exercise_api(request=request)
        response.raise_for_status()
        response_data: CreateExerciseResponseDict = response.json()
        return response_data

    def get_exercise_api(self, exercise_id: str) -> Response:
        """Получает упражнение по его идентификатору.

        Args:
            exercise_id: Идентификатор упражнения.

        Returns:
            HTTP-ответ API с данными упражнения.
        """
        return self.get(f"/api/v1/exercises/{exercise_id}")

    def get_exercise(self, exercise_id: str) -> GetExerciseResponseDict:
        """Получает упражнение по его идентификатору и возвращает его данные.

        Args:
            exercise_id: Идентификатор упражнения.

        Returns:
            Данные упражнения.
        """
        response = self.get_exercise_api(exercise_id=exercise_id)
        response.raise_for_status()
        response_data: GetExerciseResponseDict = response.json()
        return response_data

    def update_exercise_api(self, exercise_id: str, request: UpdateExerciseRequestDict) -> Response:
        """Обновляет существующее упражнение.

        Args:
            exercise_id: Идентификатор упражнения.
            request: Данные для обновления упражнения.

        Returns:
            HTTP-ответ API на запрос обновления упражнения.
        """
        return self.patch(f"/api/v1/exercises/{exercise_id}", json=request)

    def update_exercise(self, exercise_id: str, request: UpdateExerciseRequestDict) -> UpdateExerciseResponseDict:
        """Обновляет существующее упражнение и возвращает его данные.

        Args:
            exercise_id: Идентификатор упражнения.
            request: Данные для обновления упражнения.

        Returns:
            Данные обновленного упражнения.
        """
        response = self.update_exercise_api(exercise_id=exercise_id, request=request)
        response.raise_for_status()
        response_data: UpdateExerciseResponseDict = response.json()
        return response_data

    def delete_exercise_api(self, exercise_id: str) -> Response:
        """Удаляет упражнение по его идентификатору.

        Args:
            exercise_id: Идентификатор упражнения.

        Returns:
            HTTP-ответ API на запрос удаления упражнения.
        """
        return self.delete(f"/api/v1/exercises/{exercise_id}")

    def delete_exercise(self, exercise_id: str) -> None:
        """Удаляет упражнение по его идентификатору.

        Args:
            exercise_id: Идентификатор упражнения.
        """
        response = self.delete_exercise_api(exercise_id=exercise_id)
        response.raise_for_status()


def get_exercises_client(user: AuthenticationUserDict) -> ExercisesClient:
    """Создает API-клиент для работы с упражнениями.

    Args:
        user: Данные пользователя для аутентификации.

    Returns:
        Авторизованный экземпляр ExercisesClient.
    """
    return ExercisesClient(client=get_private_http_client(user))
