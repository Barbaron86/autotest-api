from clients.private_http_builder import AuthenticationUserDict
from clients.users.private_users_client import get_private_users_client
from clients.users.public_users_client import CreateUserRequestDict, get_public_users_client
from tools.fakers import get_random_email

public_users_client = get_public_users_client()

create_user_request = CreateUserRequestDict(
    email=get_random_email(), password="string", lastName="string", firstName="string", middleName="string"
)

create_user_response_data = public_users_client.create_user(request=create_user_request)
print(create_user_response_data)

authentication_user = AuthenticationUserDict(
    email=create_user_request["email"], password=create_user_request["password"]
)
private_users_client = get_private_users_client(user=authentication_user)

get_user_response_data = private_users_client.get_user(user_id=create_user_response_data["user"]["id"])
print(get_user_response_data)
