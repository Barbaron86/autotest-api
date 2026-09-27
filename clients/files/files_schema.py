from pydantic import HttpUrl

from clients.base_schema import BaseSchema


class FileSchema(BaseSchema):
    """Данные файла."""

    id: str
    filename: str
    directory: str
    url: HttpUrl


class CreateFileRequestSchema(BaseSchema):
    """Запрос на создание файла."""

    filename: str
    directory: str
    upload_file: str


class CreateFileResponseSchema(BaseSchema):
    """Ответ на создание файла."""

    file: FileSchema
