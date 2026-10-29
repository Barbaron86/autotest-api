from typing import Any

import allure
from loguru import logger

from clients.base_schema import BaseSchema
from clients.error_schema import InternalErrorResponseSchema, ValidationErrorResponseSchema, ValidationErrorSchema
from tools.assertions.base import assert_equal, assert_lens
from tools.error_types import ValidationErrorType


class ValidationErrorExpectation(BaseSchema):
    """Ожидаемые признаки ошибки, отдельные от схемы фактического ответа.

    Context сравнивается, если явно передан, включая явный None.
    Message сравнивается только при заданном тексте бизнес-причины.
    """

    type: ValidationErrorType
    location: list[str | int]
    input: Any
    context: dict[str, Any] | None = None
    message: str | None = None


@allure.step("Check validation error")
def assert_validation_error(actual: ValidationErrorSchema, expected: ValidationErrorExpectation) -> None:
    """Проверяет соответствие ошибки валидации ожидаемой.

    Args:
        actual: Фактическая ошибка валидации.
        expected: Ожидаемые признаки ошибки и при необходимости бизнес-причина.

    Raises:
        AssertionError: Если хотя бы один проверяемый признак ошибки не совпадает.
    """
    logger.info("🔎 Check validation error")
    assert_equal(actual.type, expected.type, name="type")
    assert_equal(actual.input, expected.input, name="input")
    if "context" in expected.model_fields_set:
        assert_equal(actual.context, expected.context, name="context")
    if expected.message is not None:
        assert_equal(actual.message, expected.message, name="message")
    assert_equal(actual.location, expected.location, name="location")


@allure.step("Check validation error response")
def assert_validation_error_response(
    actual: ValidationErrorResponseSchema,
    expected: list[ValidationErrorExpectation],
) -> None:
    """Проверяет количество и содержимое ошибок валидации API.

    Args:
        actual: Фактический ответ API с ошибками валидации.
        expected: Ожидаемые ошибки в порядке их получения.

    Raises:
        AssertionError: Если количество, порядок или проверяемые признаки ошибок не совпадают.
    """
    logger.info("🔎 Check validation error response")
    assert_lens(actual.detail, expected, "details")

    for index, detail in enumerate(expected):
        assert_validation_error(actual=actual.detail[index], expected=detail)


@allure.step("Check internal error response")
def assert_internal_error_response(
    actual: InternalErrorResponseSchema,
    expected: InternalErrorResponseSchema,
) -> None:
    """Проверяет соответствие сообщения об ошибке API ожидаемому.

    Args:
        actual: Фактический ответ API с сообщением об ошибке.
        expected: Ожидаемый ответ с сообщением об ошибке.

    Raises:
        AssertionError: Если сообщения об ошибке не совпадают.
    """
    logger.info("🔎 Check internal error response")
    assert_equal(actual.detail, expected.detail, name="detail")
