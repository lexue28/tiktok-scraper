from typing import Self

from tiktok.models.params.base import TikTokParams


class SearchParams(TikTokParams):
    """Parameters for the TikTok search endpoint."""

    keyword: str
    """The keyword to search for."""

    @classmethod
    def with_keyword(cls, keyword: str, params: TikTokParams) -> Self:
        """Create a new SearchParams instance with the given keyword and base parameters."""
        return cls(**params.model_dump(by_alias=True, exclude_unset=True), keyword=keyword)
