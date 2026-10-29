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
| Test examples | [tests/courses/test_courses.py](tests/courses/test_courses.py): status, domain assertions, JSON schema checks and reporting. Negative file cases in [tests/files/test_files.py](tests/files/test_files.py) pair with [tools/assertions/files.py](tools/assertions/files.py). Apply the rules below when extending these patterns. |
| pytest / Allure | [pyproject.toml](pyproject.toml), [fixtures/allure.py](fixtures/allure.py), [tools/allure/](tools/allure/): discovery, markers, metadata and environment attachment. |
| Swagger Coverage | [clients/api_coverage.py](clients/api_coverage.py): tracker for `api-course`; domain methods use its decorators. Output locations are configured in [.env.example](.env.example). |

## Local conventions

- Domain `*_api` methods expose raw responses for status and negative-case checks; convenience wrappers validate successful responses and are suitable for setup.
- Preserve PATCH omission versus explicit null and falsy values. Inspect raw JSON when exact wire types matter, even with strict Pydantic parsing.
- Use existing status/domain assertions and schema validation. Derive expectations from the contract, inputs or independent setup state; existing tests illustrate conventions.
- Tests live in `tests/<domain>/test_*.py`. Registered markers: `users`, `authentication`, `regression`, `files`, `courses`, `exercises`; reuse existing Allure titles, hierarchy, tags and stories.
- Client fixture teardown closes HTTP connections. Entity-creating fixtures such as `function_course` do not delete created records; do not assume automatic server-side cleanup or parallel isolation.

## Test authoring and review rules for this repository

These choices are specific to `autotest-api`. Apply them when adding or changing its tests; other projects use their own documented conventions.

### Scenario data and control flow

- Obtain scenario data from existing request-schema defaults, generators, named constants, fixtures or fixture factories. Keep literal credentials, arbitrary sample values, string construction and fallback branches out of test methods.
- Prepare boundary and invalid inputs through named data or fixtures/factories. Preserve deterministic conditions such as a nonzero initial index, an invalid score range or a password different from the saved password; random generation must not weaken the scenario.
- Put data-selection loops and conditional generation in the relevant data/fixture layer, and field/list comparison loops in assertions. Test methods should expose the business sequence without manual retry loops or repeated low-level validation blocks.

### Request and response names

- Name local request and response variables in test methods after the client operation and entity: `create_course_request`, `create_course_response`, `get_exercise_response`. Use the operation name for authentication, such as `login_request` or `refresh_response`.
- Distinguish the HTTP response (`get_exercise_response`), parsed schema (`get_exercise_response_data`) and raw JSON (`get_exercise_response_json`). Name query objects after the operation, such as `get_courses_query`; avoid bare `request`, `response`, `response_data`, `response_json` or `query` locals.
- When several calls need distinct names, add the meaningful role or stage, such as `get_deleted_user_response` and `get_observer_user_response`. Existing client/assertion parameter names and fixture object fields follow their established interfaces.

### Expected API errors

- Keep validation error identifiers in `ValidationErrorType(StrEnum)`. For standard framework errors, compare status, type, location, input and meaningful context parameters such as `max_length`; do not construct or compare framework/parser wording in `msg` or text-only `ctx.error`.
- Keep `msg` required and non-nullable in the actual response schema. Describe test expectations separately so omitting an expected message never weakens response validation. Compare context when explicitly specified in the expectation; omission does not assert that context is absent.
- Preserve a specific business rejection reason when the response has only a text `detail` or a generic type such as `value_error`. Keep static business messages in `ApiErrorMessage(StrEnum)` and use them from domain assertions. Do not remove such comparisons merely because the HTTP status matches; do not introduce message-formatting templates for standard errors.
- For business details containing a variable identifier, use a static `ApiErrorPattern(StrEnum)` with full matching and compare the captured identifier to the sent input. This avoids constructing an expected message while preserving its reason and identity checks; it does not apply to standard framework wording.
- Do not duplicate expected business message literals. Diagnostic assertion text, logs and Allure titles are separate from expected server messages. Verify type/message values against the applicable contract/version; enums centralize expectations and do not establish correctness.

### Assertions

- Extend the existing `tools/assertions/base.py`, `tools/assertions/errors.py` and domain assertion modules. Keep detailed error models, expected response construction, field comparisons and raw JSON checks in appropriately named assertion helpers.
- Keep the operation, status assertion before parsing, and calls to domain/schema assertions visible in the test. Preserve exact wire types, missing versus null/falsy values, independent expectations and required postconditions when extracting helpers.
- Reuse existing comparisons and Allure steps. Add a helper for a concrete domain check; keep its interface focused and avoid a generic assertion framework or flag-heavy helper.

### Prerequisite entities

- Create prerequisite entities in function-scoped fixtures or fixture factories, reusing the existing clients and request/response fixture objects. Provide explicit initial-state variants when the scenario needs them.
- Each entity-creating fixture validates its own creation response against the sent request with the existing domain assertion before returning data. Tests and dependent fixtures rely on this guarantee instead of repeating the parent's creation check. Keep scenario-specific preconditions and baseline GET checks in the relevant fixture variant.
- Keep the API operation under test in the test method: for example, a create test performs its own create request. Fixtures may supply its request data and prerequisite entities.
- Use a fixture factory when a scenario needs several independent entities. Preserve ownership, authenticated observer identity and the documented teardown behavior; do not hide assertions about the operation under test in setup.

### Review expectations

- Review changed tests against all topics above as well as behavioral correctness. Report concrete deviations with file/line and the applicable project rule; distinguish functional defects from structure/readability findings. Passing tests or no discovered functional defect does not settle compliance with these project rules.

## Verification and side effects

- Use existing installed tooling. A focused static example is `poetry run ruff check --no-cache tests/courses/test_courses.py`; adapt paths to changed files.
- A focused execution example is `poetry run pytest tests/courses/test_courses.py -m courses`, only within task authorization and against an approved test API with the configured `.env` and required test data. Do not provision or start services automatically.
- pytest enables strict configuration/markers and writes `allure-results`; `--clean-alluredir` clears previous Allure output. The session fixture also writes Allure environment properties.
- Swagger Coverage uses `coverage-results`, `coverage-history.json`, `coverage.html` and `coverage-report.json` by default. Tracker initialization occurs on import; consult configuration before collection/import or coverage commands. Do not clear or generate reports unless required.
- [clients/event_hooks.py](clients/event_hooks.py) logs requests and attaches cURL data. Treat logs and reports as potentially sensitive; avoid exposing real credentials or publishing attachments without checking their contents.

Keep reusable AQA procedures in the installed Skill and personal rules in global instructions. This file supplies repository context, not a separate planning, debugging or review workflow.
