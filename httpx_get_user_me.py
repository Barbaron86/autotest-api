import httpx


login_payload = {
     "email": "user@example.com",
     "password": "your_password"
}

login_response = httpx.post("http://localhost:8000/api/v1/authentication/login", json=login_payload)
login_response_data = login_response.json()

print("Login status code: ", login_response.status_code)
print("Response: ", login_response_data)

access_token = login_response_data["token"]["accessToken"]

get_me_response = httpx.get("http://localhost:8000/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"})

print("Get me status code: ", get_me_response.status_code)
print("Get me response: ", get_me_response.json())


