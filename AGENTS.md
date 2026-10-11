# Project context: autotest-api

Python >=3.12 API tests for API Course, using synchronous HTTPX, Pydantic v2 and pytest. Reuse the existing framework; ordinary test tasks do not include dependency, CI or infrastructure changes unless requested.

## Context pointers

Read only the pointers relevant to the task. Paths below are relative to this repository.

| Context | Pointer and responsibility |
|---|---|
| Overview / configuration | [README.md](README.md), [config.py](config.py), [.env.example](.env.example): settings and environment names; never copy credentials. |
| API contract | The tested application's OpenAPI, configured through `SWAGGER_COVERAGE_SERVICES[].swagger_url`; the example points to `http://localhost:8001/openapi.json`. [tools/routes.py](tools/routes.py) defines client routes. Models and tests supplement the contract. |
| Transport / domain clients | [clients/api_client.py](clients/api_client.py): `ApiClient` returns HTTPX responses. [clients/public_http_builder.py](clients/public_http_builder.py) and [clients/private_http_builder.py](clients/private_http_builder.py) construct public/authenticated clients. Domain clients live under [clients/](clients/). |
| Schemas / serialization | [clients/base_schema.py](clients/base_schema.py): strict Pydantic models with field-name population and alias serialization. Domain `*_schema.py` files define requests/responses; [clients/courses/courses_client.py](clients/courses/courses_client.py) uses `model_dump(exclude_unset=True)` for PATCH. |
| Fixtures / test data | [conftest.py](conftest.py) registers [fixtures/](fixtures/). Domain fixtures create data and hold request/response pairs; [tools/fakers.py](tools/fakers.py) generates values. Inspect fixture scope and teardown before relying on isolation. |
| Assertions / validation | [tools/assertions/base.py](tools/assertions/base.py), domain assertions under [tools/assertions/](tools/assertions/), and [tools/assertions/schema.py](tools/assertions/schema.py): raw JSON validation with Draft 2020-12 and format checks. |
| Test example | [tests/courses/test_courses.py](tests/courses/test_courses.py): status, domain assertions, JSON schema checks, fixtures and reporting conventions. Read the relevant case only. |
| pytest / Allure | [pyproject.toml](pyproject.toml), [fixtures/allure.py](fixtures/allure.py), [tools/allure/](tools/allure/): discovery, markers, metadata and environment attachment. |
| Swagger Coverage | [clients/api_coverage.py](clients/api_coverage.py): tracker for `api-course`; domain methods use its decorators. Output locations are configured in [.env.example](.env.example). |

## Local conventions

- Domain `*_api` methods expose raw responses for status and negative-case checks; convenience wrappers validate successful responses and are suitable for setup.
- Preserve PATCH omission versus explicit null and falsy values. Inspect raw JSON when exact wire types matter, even with strict Pydantic parsing.
- Use existing status/domain assertions and schema validation. Derive expectations from the contract, inputs or independent setup state; existing tests illustrate conventions.
- Tests live in `tests/<domain>/test_*.py`. Registered markers: `users`, `authentication`, `regression`, `files`, `courses`, `exercises`; reuse existing Allure titles, hierarchy, tags and stories.
- Client fixture teardown closes HTTP connections. Entity-creating fixtures such as `function_course` do not delete created records; do not assume automatic server-side cleanup or parallel isolation.

## Verification and side effects

- Use existing installed tooling. A focused static example is `poetry run ruff check --no-cache tests/courses/test_courses.py`; adapt paths to changed files.
- A focused execution example is `poetry run pytest tests/courses/test_courses.py -m courses`, only within task authorization and against an approved test API with the configured `.env` and required test data. Do not provision or start services automatically.
- pytest enables strict configuration/markers and writes `allure-results`; `--clean-alluredir` clears previous Allure output. The session fixture also writes Allure environment properties.
- Swagger Coverage uses `coverage-results`, `coverage-history.json`, `coverage.html` and `coverage-report.json` by default. Tracker initialization occurs on import; consult configuration before collection/import or coverage commands. Do not clear or generate reports unless required.
- [clients/event_hooks.py](clients/event_hooks.py) logs requests and attaches cURL data. Treat logs and reports as potentially sensitive; avoid exposing real credentials or publishing attachments without checking their contents.

Keep reusable AQA procedures in the installed Skill and personal rules in global instructions. This file supplies repository context, not a separate planning, debugging or review workflow.
