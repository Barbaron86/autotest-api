from pydantic import Field

from clients.base_schema import BaseSchema


class ExerciseSchema(BaseSchema):
    """Данные упражнения."""

    id: str
    title: str
    description: str
    course_id: str = Field(alias="courseId")
    max_score: int | None = Field(alias="maxScore")
    min_score: int | None = Field(alias="minScore")
    order_index: int = Field(default=0, alias="orderIndex")
    estimated_time: str | None = Field(alias="estimatedTime")


class GetExerciseResponseSchema(BaseSchema):
    """Ответ на получение упражнения."""

    exercise: ExerciseSchema


class GetExercisesResponseSchema(BaseSchema):
    """Ответ на получение списка упражнений."""

    exercises: list[ExerciseSchema]


class GetExercisesRequestSchema(BaseSchema):
    """Query-параметры для получения списка упражнений."""

    course_id: str = Field(alias="courseId")


class CreateExerciseRequestSchema(BaseSchema):
    """Запрос на создание упражнения."""

    title: str
    description: str
    course_id: str = Field(alias="courseId")
    max_score: int | None = Field(alias="maxScore")
    min_score: int | None = Field(alias="minScore")
    order_index: int = Field(default=0, alias="orderIndex")
    estimated_time: str | None = Field(alias="estimatedTime")


class CreateExerciseResponseSchema(BaseSchema):
    """Ответ на создание упражнения."""

    exercise: ExerciseSchema


class UpdateExerciseRequestSchema(BaseSchema):
    """Запрос на обновление упражнения."""

    title: str | None = None
    description: str | None = None
    max_score: int | None = Field(default=None, alias="maxScore")
    min_score: int | None = Field(default=None, alias="minScore")
    order_index: int | None = Field(default=None, alias="orderIndex")
    estimated_time: str | None = Field(default=None, alias="estimatedTime")


class UpdateExerciseResponseSchema(BaseSchema):
    """Ответ на обновление упражнения."""

    exercise: ExerciseSchema
