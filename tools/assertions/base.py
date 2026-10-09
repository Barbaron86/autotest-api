from collections.abc import Sized
from typing import Any

import allure
from loguru import logger


@allure.step("Check that response status code equals to {expected}")
def assert_status_code(actual: int, expected: int) -> None:
    """Проверяет соответствие фактического HTTP-статуса ожидаемому.

    Args:
        actual: Фактический HTTP-статус ответа.
        expected: Ожидаемый HTTP-статус ответа.

    Raises:
        AssertionError: Если фактический статус не совпадает с ожидаемым.
    """
    logger.debug("Check that response status code equals to {}", expected)
    try:
        assert actual == expected, f"Incorrect status code. Expected: {expected}. Actual: {actual}."
    except AssertionError:
        logger.error("✖ Incorrect status code. Expected: {}. Actual: {}.", expected, actual)
        raise


@allure.step("Check that {name} equals to {expected}")
def assert_equal(actual: Any, expected: Any, name: str) -> None:
    """Проверяет равенство фактического и ожидаемого значений.

    Args:
        actual: Фактическое значение.
        expected: Ожидаемое значение.
        name: Название проверяемого значения.

    Raises:
        AssertionError: Если фактическое значение не совпадает с ожидаемым.
    """
    logger.debug('Check equality of "{}"', name)
    try:
        assert actual == expected, f"Incorrect value: {name}. Expected value: {expected!r}. Actual: {actual!r}."
    except AssertionError:
        logger.error('✖ Incorrect value: "{}".', name)
        raise


@allure.step("Check that {name} is true")
def assert_is_true(actual: Any, name: str) -> None:
    """Проверяет, что фактическое значение является истинным.

    Args:
        actual: Фактическое значение.
        name: Название проверяемого значения.

    Raises:
        AssertionError: Если фактическое значение ложно.
    """
    logger.debug('Check that "{}" is true', name)
    try:
        assert actual, f"Incorrect value: {name}. Expected truthy value, got: {actual!r}."
    except AssertionError:
        logger.error('✖ Expected truthy value: "{}".', name)
        raise


def assert_lens(actual: Sized, expected: Sized, name: str) -> None:
    """Проверяет совпадение длины фактического и ожидаемого объектов.

    Args:
        actual: Фактический объект с поддержкой определения длины.
        expected: Ожидаемый объект с поддержкой определения длины.
        name: Название проверяемого объекта.

    Raises:
        AssertionError: Если длины объектов не совпадают.
    """
    with allure.step(f"Check that length of {name} equals to {len(expected)}"):
        logger.debug('Check that length of "{}" equals to {}', name, len(expected))
        try:
            assert len(actual) == len(expected), (
                f"Incorrect object length: '{name}'. Expected length: {len(expected)}. Actual: {len(actual)}."
            )
        except AssertionError as error:
            logger.error("✖ {}", error)
            raise
