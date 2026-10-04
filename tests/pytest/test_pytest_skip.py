"""Учебный пример безусловного пропуска теста из урока 8.4."""

import pytest


@pytest.mark.skip(reason="Фича в разработке")
def test_feature_in_development() -> None:
    pass
