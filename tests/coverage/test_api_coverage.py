"""Проверки сбора покрытия на границе API-клиентов и HTTPX."""

import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import indent

import pytest


@pytest.mark.regression
@pytest.mark.parametrize(
    ("request_script", "payload", "expected"),
    [
        pytest.param(
            'response = AuthenticationClient(client).login_api(LoginRequestSchema(email="user@example.com", password="secret"))',
            {"token": {"tokenType": "bearer", "accessToken": "access", "refreshToken": "refresh"}},
            {
                "name": "/api/v1/authentication/login",
                "method": "POST",
                "status_code": 200,
                "query_parameters": [],
                "is_request_covered": True,
            },
            id="json-request",
        ),
        pytest.param(
            'response = ExercisesClient(client).get_exercises_api(GetExercisesRequestSchema(courseId="course-123"))',
            {"exercises": []},
            {
                "name": "/api/v1/exercises",
                "method": "GET",
                "status_code": 200,
                "query_parameters": ["courseId"],
                "is_request_covered": False,
            },
            id="query-parameter",
        ),
        pytest.param(
            'response = ExercisesClient(client).get_exercise_api("missing-exercise")',
            {"detail": "Exercise not found"},
            {
                "name": "/api/v1/exercises/{exercise_id}",
                "method": "GET",
                "status_code": 404,
                "query_parameters": [],
                "is_request_covered": False,
            },
            id="path-template-and-error-response",
        ),
        pytest.param(
            "response = FilesClient(client).create_file_api(CreateFileRequestSchema())",
            {
                "file": {
                    "id": "file-123",
                    "filename": "image.png",
                    "directory": "tests",
                    "url": "http://api.test/static/image.png",
                }
            },
            {
                "name": "/api/v1/files",
                "method": "POST",
                "status_code": 201,
                "query_parameters": [],
                "is_request_covered": True,
            },
            id="multipart-request",
        ),
    ],
)
def test_api_client_saves_coverage(
    tmp_path: Path,
    request_script: str,
    payload: dict[str, object],
    expected: dict[str, object],
) -> None:
    """Проверяет запись реального HTTP-ответа с шаблоном пути и параметрами.

    Отдельный процесс загружает настройки до импорта декорированных клиентов.
    HTTPX MockTransport заменяет только сервер; сбор и запись покрытия реальны.

    Args:
        tmp_path: Отдельный каталог результатов для данного сценария.
        request_script: Вызов публичного метода API-клиента.
        payload: Тело ответа тестового HTTP-сервера.
        expected: Ожидаемые данные покрытия согласно контракту API.

    Raises:
        AssertionError: Если ответ изменился или данные покрытия неверны.
        subprocess.CalledProcessError: Если вызов клиента завершился ошибкой.
    """
    script = f"""
import json
import httpx
from clients.authentication.authentication_client import AuthenticationClient
from clients.authentication.authentication_schema import LoginRequestSchema
from clients.exercises.exercises_client import ExercisesClient
from clients.exercises.exercises_schema import GetExercisesRequestSchema
from clients.files.files_client import FilesClient
from clients.files.files_schema import CreateFileRequestSchema

payload = json.loads({json.dumps(payload)!r})
transport = httpx.MockTransport(lambda request: httpx.Response({expected["status_code"]}, json=payload))
with httpx.Client(base_url="http://api.test", transport=transport) as client:
{indent(request_script, "    ")}
    assert response.status_code == {expected["status_code"]}
    assert response.json() == payload
"""
    subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[2],
        env={**os.environ, "SWAGGER_COVERAGE_RESULTS_DIR": str(tmp_path)},
        check=True,
        capture_output=True,
        text=True,
    )

    results = list(tmp_path.glob("*.json"))
    assert len(results) == 1, "Один API-вызов должен создать одну запись покрытия"
    coverage = json.loads(results[0].read_text(encoding="utf-8"))
    assert coverage == {**expected, "service": "api-course", "is_response_covered": True}
