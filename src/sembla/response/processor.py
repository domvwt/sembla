import json
from typing import Any, Dict, Type, TypeVar

from sembla.schemas.base import BaseSchema

T = TypeVar("T", bound=BaseSchema)


def parse_json_response(response: str, schema: T) -> T:
    """Parse `response` as JSON and validate it against `schema`."""
    return schema.parse_raw(response)
