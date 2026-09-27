from pydantic import EmailStr, Field

from clients.base_schema import BaseSchema


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

    email: EmailStr
    password: str
    last_name: str = Field(alias="lastName")
    first_name: str = Field(alias="firstName")
    middle_name: str = Field(alias="middleName")


class CreateUserResponseSchema(BaseSchema):
    """Ответ на создание пользователя."""

    user: UserSchema
