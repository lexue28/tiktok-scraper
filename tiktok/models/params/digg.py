from typing import Self

from tiktok.models.params.base import TikTokParams
from tiktok.models.types import AwemeId


class DiggParams(TikTokParams):
    """Parameters for the TikTok dig endpoint."""

    aweme_id: AwemeId
    """The ID of the video to dig."""

    type: int
    """The type of dig to perform. 1 for like, 0 for unlike."""

    @classmethod
    def with_video_id(
        cls, video_id: AwemeId, params: TikTokParams, should_like: bool = True
    ) -> Self:
        """Create a new DiggParams instance with the given video ID and base parameters."""
        return cls(
            **params.model_dump(by_alias=True, exclude_unset=True),
            aweme_id=video_id,
            type=int(should_like),
        )
