from enum import StrEnum
from typing import TypeVar

from pydantic import BaseModel

_T = TypeVar("_T", bound=StrEnum)


class VideoActions(StrEnum):
    """
    A decision about what action to take.
    """

    NOOP = "noop"
    DIGG = "digg"
    # COMMENT = "comment"
    FOLLOW = "follow"
    LOAD = "load"


class EndOfCycleActions(StrEnum):
    """
    A decision about what action to take.
    """

    CONTINUE = "continue"
    SEARCH = "search"
    QUIT = "quit"


class VideoAction(BaseModel):
    """
    A decision about what action to take.
    """

    action: VideoActions
    reason: str


class VideoDecision(BaseModel):
    """
    A decision about what action to take.
    """

    actions: dict[str, VideoAction]


class EndOfCycleDecision(BaseModel):
    """
    A decision about what action to take.
    """

    action: EndOfCycleActions
    search_keyword: str | None = None
