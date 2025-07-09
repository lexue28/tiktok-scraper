from typing import Self

from tiktok.models.params.base import TikTokParams
from tiktok.models.types import AwemeId


class CommentParams(TikTokParams):
    """Parameters for the TikTok comment endpoint."""

    aweme_id: AwemeId
    """The ID of the video to comment for."""

    @classmethod
    def with_video_id(cls, video_id: AwemeId, params: TikTokParams) -> Self:
        """Create a new CommentParams instance with the given video ID and base parameters."""
        return cls(**params.model_dump(by_alias=True, exclude_unset=True), aweme_id=video_id)


class CommentDiggParams(TikTokParams):
    """Parameters for the TikTok comment endpoint."""

    cid: AwemeId
    """The ID of the comment to digg."""

    digg_type: int
    """The type of the comment to digg. 1: digg, 0: undo digg."""

    @classmethod
    def with_comment_id(
        cls, comment_id: AwemeId, params: TikTokParams, should_like: bool = True
    ) -> Self:
        """Create a new CommentParams instance with the given comment ID and base parameters."""
        return cls(
            **params.model_dump(by_alias=True, exclude_unset=True),
            cid=comment_id,
            digg_type=int(should_like),
        )


class CommentPublishParams(TikTokParams):
    """Parameters for the TikTok comment publish endpoint."""

    aweme_id: AwemeId
    """The ID of the video to comment for."""

    text: str
    """The text of the comment to publish."""

    @classmethod
    def with_video_id(cls, comment: str, video_id: AwemeId, params: TikTokParams) -> Self:
        """Create a new CommentPublishParams instance with the given video ID and base parameters."""
        return cls(
            **params.model_dump(by_alias=True, exclude_unset=True), aweme_id=video_id, text=comment
        )
