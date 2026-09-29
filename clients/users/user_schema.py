from pydantic import EmailStr, Field

from clients.base_schema import BaseSchema
from tools.fakers import fake


class UserSchema(BaseSchema):
    """Данные пользователя."""

    id: str
    email: EmailStr
    last_name: str = Field(alias="lastName")
    first_name: str = Field(alias="firstName")
    middle_name: str = Field(alias="middleName")


class UpdateUserRequestSchema(BaseSchema):
    """Запрос на обновление данных пользователя."""

    email: EmailStr | None = None
    last_name: str | None = Field(default=None, alias="lastName")
    first_name: str | None = Field(default=None, alias="firstName")
    middle_name: str | None = Field(default=None, alias="middleName")


class UpdateUserResponseSchema(BaseSchema):
    """Ответ на обновление данных пользователя."""

    user: UserSchema


class GetUserResponseSchema(BaseSchema):
    """Ответ на получение данных пользователя."""

    user: UserSchema


class CreateUserRequestSchema(BaseSchema):
    """Запрос на создание пользователя."""

    email: EmailStr = Field(default_factory=fake.email)
    password: str = Field(default_factory=fake.password)
    last_name: str = Field(alias="lastName", default_factory=fake.last_name)
    first_name: str = Field(alias="firstName", default_factory=fake.first_name)
    middle_name: str = Field(alias="middleName", default_factory=fake.middle_name)


class CreateUserResponseSchema(BaseSchema):
    """Ответ на создание пользователя."""

    user: UserSchema
