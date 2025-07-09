import inspect
from typing import Any, Self
from unittest.mock import Mock


def create_mock(spec: object) -> Mock:
    """
    Create a mock from the given specification raising errors for non-specifically overridden methods.

    `object` is used as a type for the Spec for compatibility with the spec_set of unittest.Mock;
    this is needed in case we want to create mocks from Protocols, which are not classes.
    """
    mock = Mock(spec_set=spec)

    methods = [name for name, _ in inspect.getmembers(spec, predicate=inspect.isfunction)]
    for method in filter(lambda name: not name.startswith("_"), methods):
        name = getattr(spec, "__name__")
        error = f"Mock did not override method '{method}' for class '{name}'"
        setattr(mock, method, Mock(side_effect=AttributeError(error)))

    return mock


class FakeIO:
    """Class to mock a file-like object."""

    def __init__(self, content: str = ""):
        self.content = content
        self.position = 0

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass

    async def read(self) -> str:
        return self.content

    async def write(self, data: str) -> None:
        split = [self.content[: self.position], self.content[self.position + 1 :]]
        self.content = split[0] + data + split[1]

    async def tell(self) -> int:
        return len(self.content)

    async def seek(self, pos: int) -> None:
        self.position = pos


class FakeIOReader:
    """Class to mock aiofiles.open."""

    def __init__(self, files: dict[str, FakeIO]):
        self.files = files

    def __call__(self, path: str, mode: str) -> FakeIO:
        if mode == "r+" and str(path) not in self.files:
            raise FileNotFoundError
        if str(path) not in self.files:
            self.files[str(path)] = FakeIO()
        return self.files[str(path)]
