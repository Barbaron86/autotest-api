import allure
from httpx import Response

from clients.api_client import ApiClient
from clients.api_coverage import tracker
from clients.courses.courses_schema import (
    CreateCourseRequestSchema,
    CreateCourseResponseSchema,
    GetCoursesQuerySchema,
    UpdateCourseRequestSchema,
)
from clients.private_http_builder import AuthenticationUserSchema, get_private_http_client
from tools.routes import APIRoutes


class CoursesClient(ApiClient):
    """API-клиент для работы с курсами."""

    @allure.step("Get courses")
    @tracker.track_coverage_httpx(APIRoutes.COURSES)
    def get_courses_api(self, query: GetCoursesQuerySchema) -> Response:
        """Выполняет запрос на получение списка курсов.

        Args:
            query: Query-параметры для получения курсов.

        Returns:
            HTTP-ответ API со списком курсов.
        """
        return self.get(APIRoutes.COURSES, params=query.model_dump())

    @allure.step("Get course by id {course_id}")
    @tracker.track_coverage_httpx(f"{APIRoutes.COURSES}/{{course_id}}")
    def get_course_api(self, course_id: str) -> Response:
        """Выполняет запрос на получение курса.

        Args:
            course_id: Идентификатор курса.

        Returns:
            HTTP-ответ API с данными курса.
        """
        return self.get(f"{APIRoutes.COURSES}/{course_id}")

    @allure.step("Create course")
    @tracker.track_coverage_httpx(APIRoutes.COURSES)
    def create_course_api(self, request: CreateCourseRequestSchema) -> Response:
        """Выполняет запрос на создание курса.

        Args:
            request: Данные для создания курса.

        Returns:
            HTTP-ответ API на запрос создания курса.
        """
        return self.post(APIRoutes.COURSES, json=request.model_dump())

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

    @allure.step("Update course by id {course_id}")
    @tracker.track_coverage_httpx(f"{APIRoutes.COURSES}/{{course_id}}")
    def update_course_api(self, course_id: str, request: UpdateCourseRequestSchema) -> Response:
        """Выполняет запрос на обновление курса.

        Args:
            course_id: Идентификатор курса.
            request: Данные для обновления курса.

        Returns:
            HTTP-ответ API на запрос обновления курса.
        """
        return self.patch(f"{APIRoutes.COURSES}/{course_id}", json=request.model_dump(exclude_unset=True))

    @allure.step("Delete course by id {course_id}")
    @tracker.track_coverage_httpx(f"{APIRoutes.COURSES}/{{course_id}}")
    def delete_course_api(self, course_id: str) -> Response:
        """Выполняет запрос на удаление курса.

        Args:
            course_id: Идентификатор курса.

        Returns:
            HTTP-ответ API на запрос удаления курса.
        """
        return self.delete(f"{APIRoutes.COURSES}/{course_id}")


def get_courses_client(user: AuthenticationUserSchema) -> CoursesClient:
    """Создает авторизованный API-клиент для работы с курсами.

    Args:
        user: Учетные данные пользователя для аутентификации.

    Returns:
        Авторизованный экземпляр CoursesClient.
    """
    return CoursesClient(client=get_private_http_client(user))
