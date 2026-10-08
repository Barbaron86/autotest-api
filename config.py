"""Настройки API-автотестов из окружения и локального файла .env."""

from pathlib import Path

from pydantic import AliasChoices, BaseModel, Field, FilePath, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class HTTPClientConfig(BaseSettings):
    """Настройки HTTP-клиента.

    Attributes:
        url: Адрес API, совместимый с переменной API_BASE_URL.
        timeout: Положительный конечный таймаут HTTP-запросов в секундах.
    """

    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: HttpUrl = Field(
        default=HttpUrl("http://localhost:8000"),
        validation_alias=AliasChoices("url", "API_BASE_URL"),
    )
    timeout: float = Field(default=100, gt=0, allow_inf_nan=False)

    @property
    def client_url(self) -> str:
        """Возвращает адрес API в строковом формате для HTTPX."""
        return str(self.url)

    @field_validator("url")
    @classmethod
    def validate_base_url(cls, value: HttpUrl) -> HttpUrl:
        """Отклоняет компоненты URL, мешающие присоединению пути запроса.

        Args:
            value: Проверенный HTTP-адрес API.

        Returns:
            Адрес API без query и fragment.

        Raises:
            ValueError: Если адрес содержит query или fragment.
        """
        if value.query is not None or value.fragment is not None:
            raise ValueError("API_BASE_URL не должен содержать query или fragment")
        return value


class TestDataConfig(BaseModel):
    """Пути к тестовым данным.

    Attributes:
        image_png_file: Существующий PNG-файл для загрузки через API.
    """

    image_png_file: FilePath = Field(default=Path("testdata/files/image.png"), validate_default=True)


class Settings(BaseSettings):
    """Настройки автотестов из окружения и файла .env.

    Attributes:
        http_client: Настройки соединения с API.
        test_data: Пути к тестовым данным.
        allure_results_dir: Каталог с результатами Allure.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter=".",
        extra="ignore",
    )

    http_client: HTTPClientConfig = Field(default_factory=HTTPClientConfig)
    test_data: TestDataConfig = Field(default_factory=TestDataConfig)
    allure_results_dir: Path = Path("allure-results")


settings = Settings()
