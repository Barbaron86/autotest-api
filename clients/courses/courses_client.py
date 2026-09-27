from httpx import Response

from clients.api_client import ApiClient
from clients.courses.courses_schema import (
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
    GetCoursesQuerySchema,
    UpdateCourseRequestSchema,
)
from clients.private_http_builder import AuthenticationUserSchema, get_private_http_client


class CoursesClient(ApiClient):
    """API-клиент для работы с курсами."""

    def get_courses_api(self, query: GetCoursesQuerySchema) -> Response:
        """Выполняет запрос на получение списка курсов.

        Args:
            query: Query-параметры для получения курсов.

        Returns:
            HTTP-ответ API со списком курсов.
        """
        return self.get("/api/v1/courses", params=query.model_dump())

    def get_course_api(self, course_id: str) -> Response:
        """Выполняет запрос на получение курса.

        Args:
            course_id: Идентификатор курса.

        Returns:
            HTTP-ответ API с данными курса.
        """
        return self.get(f"/api/v1/courses/{course_id}")

    def create_course_api(self, request: CreateCourseRequestSchema) -> Response:
        """Выполняет запрос на создание курса.

        Args:
            request: Данные для создания курса.

        Returns:
            HTTP-ответ API на запрос создания курса.
        """
        return self.post("/api/v1/courses", json=request.model_dump())

    def create_course(self, request: CreateCourseRequestSchema) -> CreateCourseResponseSchema:
        """Создает курс.

        Args:
            request: Данные для создания курса.

        Returns:
            Данные созданного курса.
        """
        response = self.create_course_api(request=request)
        response.raise_for_status()

        return CreateCourseResponseSchema.model_validate_json(response.text)

    def update_course_api(self, course_id: str, request: UpdateCourseRequestSchema) -> Response:
        """Выполняет запрос на обновление курса.

        Args:
            course_id: Идентификатор курса.
            request: Данные для обновления курса.

        Returns:
            HTTP-ответ API на запрос обновления курса.
        """
        return self.patch(f"/api/v1/courses/{course_id}", json=request.model_dump(exclude_unset=True))

    def delete_course_api(self, course_id: str) -> Response:
        """Выполняет запрос на удаление курса.

        Args:
            course_id: Идентификатор курса.

        Returns:
            HTTP-ответ API на запрос удаления курса.
        """
        return self.delete(f"/api/v1/courses/{course_id}")


def get_courses_client(user: AuthenticationUserSchema) -> CoursesClient:
    """Создает авторизованный API-клиент для работы с курсами.

    Args:
        user: Учетные данные пользователя для аутентификации.

    Returns:
        Авторизованный экземпляр CoursesClient.
    """
    return CoursesClient(client=get_private_http_client(user))
