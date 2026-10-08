import allure

from clients.error_schema import InternalErrorResponseSchema, ValidationErrorResponseSchema, ValidationErrorSchema
from tools.assertions.base import assert_equal, assert_lens


@allure.step("Check validation error")
def assert_validation_error(actual: ValidationErrorSchema, expected: ValidationErrorSchema) -> None:
    """Проверяет соответствие ошибки валидации ожидаемой.

    Args:
        actual: Фактическая ошибка валидации.
        expected: Ожидаемая ошибка валидации.

    Raises:
        AssertionError: Если хотя бы одно поле ошибки не совпадает.
    """
    assert_equal(actual.type, expected.type, name="type")
    assert_equal(actual.input, expected.input, name="input")
    assert_equal(actual.context, expected.context, name="context")
    assert_equal(actual.message, expected.message, name="message")
    assert_equal(actual.location, expected.location, name="location")


@allure.step("Check validation error response")
def assert_validation_error_response(
    actual: ValidationErrorResponseSchema,
    expected: ValidationErrorResponseSchema,
) -> None:
    """Проверяет количество и содержимое ошибок валидации API.

    Args:
        actual: Фактический ответ API с ошибками валидации.
        expected: Ожидаемый ответ с ошибками валидации.

    Raises:
        AssertionError: Если количество, порядок или поля ошибок не совпадают.
    """
    assert_lens(actual.detail, expected.detail, "details")

    for index, detail in enumerate(expected.detail):
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
    assert_equal(actual.detail, expected.detail, name="detail")
