import pytest
from pydantic import BaseModel

from core.controller.base import BaseController


class UpdateSchema(BaseModel):
    name: str | None = None
    count: int | None = None


@pytest.mark.asyncio
async def test_extract_attributes_from_schema_returns_set_fields_only():
    schema = UpdateSchema(name="alpha")

    attributes = await BaseController.extract_attributes_from_schema(schema)

    assert attributes == {"name": "alpha"}


@pytest.mark.asyncio
async def test_extract_attributes_from_schema_honors_excludes():
    schema = UpdateSchema(name="alpha", count=3)

    attributes = await BaseController.extract_attributes_from_schema(
        schema,
        excludes={"count"},
    )

    assert attributes == {"name": "alpha"}
