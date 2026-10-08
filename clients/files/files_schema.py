from pydantic import Field, FilePath, HttpUrl

from clients.base_schema import BaseSchema
from config import settings
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
    upload_file: FilePath = Field(default_factory=lambda: settings.test_data.image_png_file)


class CreateFileResponseSchema(BaseSchema):
    """Ответ на создание файла."""

    file: FileSchema


class GetFileResponseSchema(BaseSchema):
    """Ответ на получение файла."""

    file: FileSchema
