import httpx
from tools.fakers import get_random_email

create_user_payload = {
    "email": get_random_email(),
    "password": "string",
    "lastName": "string",
    "firstName": "string",
    "middleName": "string"
}

create_user_response = httpx.post("http://localhost:8000/api/v1/users", json=create_user_payload)
print(create_user_response.status_code)

create_user_response_data = create_user_response.json()
print(create_user_response_data)

login_payload = {
    "email": create_user_payload["email"],
    "password": create_user_payload["password"]
}

login_response = httpx.post("http://localhost:8000/api/v1/authentication/login", json=login_payload)
print(login_response.status_code)

login_response_data = login_response.json()
print(login_response_data)

get_user_response = httpx.get(f"http://localhost:8000/api/v1/users/{create_user_response_data['user']['id']}", headers={"Authorization": f"Bearer {login_response_data['token']['accessToken']}"})
print(get_user_response.status_code)

get_user_response_data = get_user_response.json()
print(get_user_response_data)
