import re

from pydantic import BaseModel, ConfigDict


def snake_to_camel(string: str) -> str:
    """Convert a snake_case string to camelCase."""
    # Check if string is already camelCase
    if re.match(r"^[a-z]+[A-Z][a-z]+$", string):
        return string

    return re.sub(r"(_\w)", lambda m: m.group(1)[1].upper(), string)


def snake_to_pascal(string: str) -> str:
    """Convert a snake_case string to PascalCase."""
    # Check if string is already PascalCase
    if re.match(r"^[A-Z][a-z]+[A-Z][a-z]+$", string):
        return string

    return "".join(word.title() for word in string.split("_"))


class CamelizeBaseModel(BaseModel):
    """Base model that converts all snake case fields to camel case."""

    model_config = ConfigDict(alias_generator=snake_to_camel, populate_by_name=True)


class PascalizeBaseModel(BaseModel):
    """Base model that converts all snake case fields to Pascal case."""

    model_config = ConfigDict(alias_generator=snake_to_pascal, populate_by_name=True)
