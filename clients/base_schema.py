from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая схема API."""

    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
    )
