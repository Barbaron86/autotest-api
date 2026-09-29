from collections.abc import Mapping
from typing import Any

from jsonschema import Draft202012Validator, validate


def validate_json_schema(
    instance: Any,
    schema: Mapping[str, Any],
) -> None:
    """Проверяет данные на соответствие JSON Schema.

    Использует спецификацию JSON Schema Draft 2020-12 и выполняет
    дополнительную проверку значений с указанным `format`.

    Args:
        instance: Данные, которые необходимо проверить.
        schema: JSON Schema, описывающая ожидаемую структуру данных.

    Raises:
        jsonschema.exceptions.ValidationError:
            Если данные не соответствуют JSON Schema.
        jsonschema.exceptions.SchemaError:
            Если переданная JSON Schema некорректна.
    """
    validate(
        instance=instance,
        schema=schema,
        cls=Draft202012Validator,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
