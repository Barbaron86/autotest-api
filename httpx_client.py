import httpx

login_payload = {"email": "4user@example.com", "password": "string"}

login_response = httpx.post("http://localhost:8000/api/v1/authentication/login", json=login_payload)
print(login_response.status_code)

login_response_data = login_response.json()
print(login_response_data)

client = httpx.Client(
    base_url="http://localhost:8000",
    timeout=10,
    headers={"Authorization": f"Bearer {login_response_data['token']['accessToken']}"}
)

get_user_me_response = client.get("/api/v1/users/me")
get_user_me_response_data = get_user_me_response.json()
print(get_user_me_response_data)