from pydantic import EmailStr, Field

from clients.base_schema import BaseSchema


class TokenSchema(BaseSchema):
    """Данные токена авторизации."""

    token_type: str = Field(..., alias="tokenType")
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")


class LoginRequestSchema(BaseSchema):
    """Запрос на аутентификацию."""

    email: EmailStr
    password: str


class LoginResponseSchema(BaseSchema):
    """Ответ на аутентификацию."""

    token: TokenSchema


class RefreshRequestSchema(BaseSchema):
    """Запрос на обновление токена."""

    refresh_token: str = Field(alias="refreshToken")
