"""Сведения об окружении для отчета Allure."""

import platform
import sys
from pathlib import Path

from config import settings


def create_allure_environment_file(results_dir: Path) -> None:
    """Сохраняет настройки, версию ОС и Python рядом с результатами Allure.

    Args:
        results_dir: Каталог результатов текущего запуска pytest.
    """
    environment = settings.model_dump()
    environment["allure_results_dir"] = results_dir
    environment.update(os_info=f"{platform.system()}, {platform.release()}", python_version=sys.version)
    content = "\n".join(f"{key}={value}" for key, value in environment.items())
    (results_dir / "environment.properties").write_text(content, encoding="utf-8")
