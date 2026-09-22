from typing import TypedDict

from httpx import Response

from clients.api_client import ApiClient


class GetCoursesQueryDict(TypedDict):
    """Описание структуры query-параметров для получения курсов."""

    userId: str


class CreateCourseRequestDict(TypedDict):
    """Описание структуры запроса на создание курса."""

    title: str
    maxScore: int | None
    minScore: int | None
    description: str
    estimatedTime: str | None
    previewFileId: str
    createdByUserId: str


class UpdateCourseRequestDict(TypedDict):
    """Описание структуры запроса на обновление курса."""

    title: str | None
    maxScore: int | None
    minScore: int | None
    description: str | None
    estimatedTime: str | None


class CoursesClient(ApiClient):
    """API-клиент для работы с курсами."""

    def get_courses_api(self, query: GetCoursesQueryDict) -> Response:
        """Получает список курсов.

        Args:
            query: Query-параметры для фильтрации списка курсов.

        Returns:
            HTTP-ответ API со списком курсов.
        """
        return self.get("/api/v1/courses", params=query)

    def get_course_api(self, course_id: str) -> Response:
        """Получает курс по его идентификатору.

        Args:
            course_id: Идентификатор курса.

        Returns:
            HTTP-ответ API с данными курса.
        """
        return self.get(f"/api/v1/courses/{course_id}")

    def create_course_api(self, request: CreateCourseRequestDict) -> Response:
        """Создает новый курс.

        Args:
            request: Данные для создания курса.

        Returns:
            HTTP-ответ API на запрос создания курса.
        """
        return self.post("/api/v1/courses", json=request)

    def update_course_api(self, course_id: str, request: UpdateCourseRequestDict) -> Response:
        """Обновляет существующий курс.

        Args:
            course_id: Идентификатор курса.
            request: Данные для обновления курса.

        Returns:
            HTTP-ответ API на запрос обновления курса.
        """
        return self.patch(f"/api/v1/courses/{course_id}", json=request)

    def delete_course_api(self, course_id: str) -> Response:
        """Удаляет курс по его идентификатору.

        Args:
            course_id: Идентификатор курса.

        Returns:
            HTTP-ответ API на запрос удаления курса.
        """
        return self.delete(f"/api/v1/courses/{course_id}")
