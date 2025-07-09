from typing import Self

from pydantic import Field

from tiktok.models.params.base import TikTokParams
from tiktok.models.types import AwemeId


class VideoDetailsParams(TikTokParams):
    """Parameters for the TikTok video details endpoint."""

    item_id: AwemeId = Field(alias="itemId")
    """The ID of the video to get details for."""

    @classmethod
    def with_video_id(cls, video_id: AwemeId, params: TikTokParams) -> Self:
        """Create a new DiggParams instance with the given video ID and base parameters."""
        return cls(
            **params.model_dump(by_alias=True, exclude_unset=True),
            itemId=video_id,
        )
