from pydantic import Field, HttpUrl

from clients.base_schema import BaseSchema
from tools.fakers import fake


class FileSchema(BaseSchema):
    """Данные файла."""

    id: str
    filename: str
    directory: str
    url: HttpUrl


class CreateFileRequestSchema(BaseSchema):
    """Запрос на создание файла."""

    filename: str = Field(default_factory=lambda: f"{fake.uuid4()}.png")
    directory: str = Field(default="tests")
    upload_file: str = Field(default="./testdata/files/image.png")


class CreateFileResponseSchema(BaseSchema):
    """Ответ на создание файла."""

    file: FileSchema


class GetFileResponseSchema(BaseSchema):
    """Ответ на получение файла."""

    file: FileSchema
