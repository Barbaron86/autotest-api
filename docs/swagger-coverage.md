# Покрытие API по уроку 13

Используется `swagger-coverage-tool==0.34.0`. Версия закреплена в Poetry и
`poetry.lock`. [Репозиторий библиотеки](https://github.com/Nikita-Filonov/swagger-coverage-tool).

Общий трекер находится в `clients/api_coverage.py`. Типизированный адаптер
передаёт работу библиотечному декоратору, сохраняя сигнатуры методов для mypy.
Декораторы добавлены к 20 методам, возвращающим `httpx.Response`, во всех
API-клиентах, включая пять методов `ExercisesClient` из практического задания.
Шаблоны путей строятся через `APIRoutes` и совпадают с OpenAPI.

## Локальный запуск

Установите зависимости командой `poetry install --no-root`. Если `.env` ещё нет,
скопируйте `.env.example` в `.env`. Адрес `swagger_url` внутри
`SWAGGER_COVERAGE_SERVICES` должен совпадать с `API_BASE_URL` и заканчиваться
на `/openapi.json`. Для Docker-стенда в примере используется порт `8001`;
при запуске API на `8000` исправьте оба адреса и `API_PORT`.

Запустите API. Для настроенного Docker-стенда:

```shell
docker compose up --build --wait
```

Из корня проекта выполните:

```shell
poetry run swagger-coverage-tool clear-results
poetry run pytest -m regression --numprocesses=2
poetry run swagger-coverage-tool save-report
```

API должен работать до окончания `save-report`: команда загружает его OpenAPI.
Откройте `coverage.html` в браузере. `coverage-report.json` содержит данные
отчёта, а `coverage-history.json` — историю последних 30 запусков.

`clear-results` удаляет промежуточные JSON-файлы предыдущего прогона из
`coverage-results`. Файл истории сохраняется. Без очистки отчёт будет учитывать
также вызовы из предыдущих прогонов. Все эти артефакты исключены из Git.

Отчёт фиксирует выполненные запросы, статусы, переданные query-параметры и
наличие тела запроса/ответа. Проверку значений и схем ответа выполняют assertions
в тестах. Процент в отчёте не означает покрытие строк кода или всех требований.

## GitHub Actions

Текущий CI устанавливает зависимости через Poetry и запускает API в Docker.
После тестов, до выключения API, workflow генерирует покрытие и загружает
артефакт `coverage-report` с HTML, JSON и файлом истории. При падении тестов
отчёт также создаётся, если успели собраться результаты.

Официальная история восстанавливается только на `push` в `main` с полным
`regression`. Она сохраняется после успешных тестов и генерации отчёта.
Используется отдельная цепочка ключей `coverage-history-official-main-regression-v1-`;
кеши прежней политики в неё не входят. Повторные попытки имеют собственные ключи.

PR и `workflow_dispatch`, включая ручной `regression` на `main`, создают
артефакт без восстановления или сохранения официальной истории. Их файл
`coverage-history.json` содержит только текущий запуск.

На успешном `push main regression` существующий job `reports` добавляет
`swagger-coverage/index.html` и `swagger-coverage/coverage-report.json` в общее
дерево Pages перед единственным publish в `gh-pages`. Workflow Summary содержит
прямую ссылку на `/swagger-coverage/`. PR сохраняет существующий coverage-раздел
Pages без изменений; ручные запуски вообще не публикуют Pages.

Интеграция проверяется реальными API-тестами `regression`: их вызовы создают
`coverage-results`, затем `save-report` строит HTML, JSON и историю до выключения
API. Отдельных тестов поведения сторонней библиотеки в этом наборе нет.
