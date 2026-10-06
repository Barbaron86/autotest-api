from typing import Any

from pydantic import Field

from clients.base_schema import BaseSchema


class ValidationErrorSchema(BaseSchema):
    """Описание ошибки валидации API.

    Attributes:
        type: Тип ошибки валидации.
        location: Путь к некорректному полю в запросе.
        message: Сообщение об ошибке.
        input: Значение, не прошедшее валидацию.
        context: Дополнительные параметры ошибки, если они переданы API.
    """

    type: str
    location: list[str | int] = Field(alias="loc")
    message: str = Field(alias="msg")
    input: Any
    context: dict[str, Any] | None = Field(default=None, alias="ctx")


class ValidationErrorResponseSchema(BaseSchema):
    """Ответ API с ошибками валидации.

    Attributes:
        detail: Список ошибок валидации запроса.
    """

    detail: list[ValidationErrorSchema]


class InternalErrorResponseSchema(BaseSchema):
    """Ответ API с сообщением об ошибке, например об отсутствии файла.

    Attributes:
        detail: Описание ошибки.
    """

    detail: str
