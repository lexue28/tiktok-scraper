from typing import Iterator, TypeVar

_T = TypeVar("_T")


def chunkize(list: list[_T], chunk_size: int) -> Iterator[list[_T]]:
    """
    Chunk a list into smaller lists of a given size.
    """
    for i in range(0, len(list), chunk_size):
        yield list[i : i + chunk_size]
