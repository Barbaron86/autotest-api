import httpx

response = httpx.get("https://jsonplaceholder.typicode.com/todos/1")
print(response.status_code)
print(response.json())

data = {
    "title": "new task",
    "completed": False,
    "userId": 1
}

response = httpx.post("https://jsonplaceholder.typicode.com/todos", json=data)

print(response.status_code)
print(response.json())

data_test = {
    "username": "test",
    "password": "test"
}
response = httpx.post("https://httpbin.org/post", data=data_test)

print(response.status_code)
print(response.json())

headers = {"Authorization": "Bearer my secret token"}
response = httpx.get("https://httpbin.org/get", headers=headers)

print(response.status_code)
print(response.request.headers)
print(response.json())

params = {"userId": 1}
response = httpx.get("https://jsonplaceholder.typicode.com/todos", params=params)

print(response.url)
print(response.json())

with open("example.txt", "rb") as file:
    files = {
        "file": ("example.txt", file),
    }

    response = httpx.post(
        "https://httpbin.org/post",
        files=files,
    )

print(response.json())

with httpx.Client() as client:
    response1 = client.get(
        "https://jsonplaceholder.typicode.com/todos/1"
    )

    response2 = client.get(
        "https://jsonplaceholder.typicode.com/todos/2"
    )

print(response1.json())
print(response2.json())

client = httpx.Client(
    headers={
        "Authorization": "Bearer my_secret_token",
    }
)

response = client.get(
    "https://httpbin.org/get"
)

print(response.json())

client.close()

try:
    response = httpx.get(
        "https://jsonplaceholder.typicode.com/invalid-url"
    )

    response.raise_for_status()

except httpx.HTTPStatusError as error:
    print(f"Ошибка запроса: {error}")

try:
    response = httpx.get(
        "https://httpbin.org/delay/5",
        timeout=2,
    )

except httpx.ReadTimeout:
    print("Запрос превысил лимит времени")
