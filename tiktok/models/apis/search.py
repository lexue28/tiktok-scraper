from typing import Any

from pydantic import BaseModel

from tiktok.models.apis.common import Extra, LogPb, User
from tiktok.models.apis.trending import TikTokVideo


class SearchUser(BaseModel):
    """The user result of a search."""

    user_info: User
    """The user result of the search."""

    position: int | None = None
    """The position of the user in the search results."""

    uniqid_position: int | None = None
    """The uniqid position of the user in the search results."""

    effects: Any | None = None
    """The effects of the user in the search results."""

    musics: Any | None = None
    """The musics of the user in the search results."""

    items: Any | None = None
    """The items of the user in the search results."""

    mix_list: Any | None = None
    """The mix list of the user in the search results."""

    challenges: Any | None = None
    """The challenges of the user in the search results."""


class SearchResult(BaseModel):
    """The result of a search."""

    type: int
    """The type of the search result."""

    item: TikTokVideo | None = None
    """The video result of the search."""

    user_list: list[SearchUser] | None = None
    """The list of user results."""

    common: dict[str, Any]
    """The common information about the search result."""


class SearchResponse(BaseModel):
    """
    Response model for the search endpoint.
    """

    qc: str | None = None
    """The query string used for the search."""

    cursor: int | None = None
    """The cursor to use for the next page of results."""

    has_more: bool | None = None
    """Whether there are more results to fetch."""

    ad_info: dict[str, Any] | None = None
    """Additional information about the search."""

    extra: Extra | None = None
    """Additional metadata about the response."""

    log_pb: LogPb | None = None
    """Logging information about the response."""

    status_code: int | None = None
    """The status code of the response."""

    global_doodle_config: dict[str, Any] | None = None
    """The global doodle configuration for the search."""

    backtrace: str | None = None
    """The backtrace of the search."""

    data: list[SearchResult] | None = None
    """The list of search results."""
