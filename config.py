"""Настройки API-автотестов из окружения и локального файла .env."""

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки соединения с тестируемым API.

    Attributes:
        base_url: Адрес API из переменной API_BASE_URL.
        timeout: Положительный конечный таймаут HTTP-запросов в секундах.
    """

    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: HttpUrl = HttpUrl("http://localhost:8000")
    timeout: float = Field(default=100, gt=0, allow_inf_nan=False)

    @field_validator("base_url")
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


settings = Settings()
