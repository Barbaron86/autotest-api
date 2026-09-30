from http import HTTPStatus

from clients.authentication.authentication_client import get_authentication_client
from clients.authentication.authentication_schema import LoginRequestSchema, LoginResponseSchema
from clients.users.public_users_client import get_public_users_client
from clients.users.user_schema import CreateUserRequestSchema
from tools.assertions.authentication import assert_login_response
from tools.assertions.base import assert_status_code
from tools.assertions.schema import validate_json_schema


def test_login() -> None:
    """Проверяет успешную аутентификацию нового пользователя.

    Создаёт пользователя с автоматически сгенерированными данными,
    выполняет вход и проверяет HTTP-статус, токены и JSON Schema ответа.
    """
    public_users_client = get_public_users_client()
    authentication_client = get_authentication_client()

    with public_users_client.client, authentication_client.client:
        create_user_request = CreateUserRequestSchema()
        public_users_client.create_user(request=create_user_request)

        login_request = LoginRequestSchema(
            email=create_user_request.email,
            password=create_user_request.password,
        )
        login_response = authentication_client.login_api(request=login_request)

        assert_status_code(actual=login_response.status_code, expected=HTTPStatus.OK)
        login_response_data = LoginResponseSchema.model_validate_json(login_response.text)
        assert_login_response(response=login_response_data)

        validate_json_schema(
            instance=login_response.json(),
            schema=LoginResponseSchema.model_json_schema(),
        )
