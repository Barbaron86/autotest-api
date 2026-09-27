from pydantic import Field

from clients.base_schema import BaseSchema
from clients.files.files_schema import FileSchema
from clients.users.user_schema import UserSchema


class CourseSchema(BaseSchema):
    """Данные курса."""

    id: str
    title: str
    max_score: int | None = Field(default=None, alias="maxScore")
    min_score: int | None = Field(default=None, alias="minScore")
    description: str
    estimated_time: str | None = Field(default=None, alias="estimatedTime")
    preview_file: FileSchema = Field(alias="previewFile")
    created_by_user: UserSchema = Field(alias="createdByUser")


class GetCoursesQuerySchema(BaseSchema):
    """Query-параметры для получения курсов."""

    user_id: str = Field(alias="userId")


class CreateCourseRequestSchema(BaseSchema):
    """Запрос на создание курса."""

    title: str
    max_score: int | None = Field(default=None, alias="maxScore")
    min_score: int | None = Field(default=None, alias="minScore")
    description: str
    estimated_time: str | None = Field(default=None, alias="estimatedTime")
    preview_file_id: str = Field(alias="previewFileId")
    created_by_user_id: str = Field(alias="createdByUserId")


class CreateCourseResponseSchema(BaseSchema):
    """Ответ на создание курса."""

    course: CourseSchema


class UpdateCourseRequestSchema(BaseSchema):
    """Запрос на обновление курса."""

    title: str | None = None
    max_score: int | None = Field(default=None, alias="maxScore")
    min_score: int | None = Field(default=None, alias="minScore")
    description: str | None = None
    estimated_time: str | None = Field(default=None, alias="estimatedTime")
