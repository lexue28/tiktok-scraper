from typing import Self

from tiktok.models.params.base import TikTokParams


class FollowParams(TikTokParams):
    """Parameters for the TikTok follow endpoint."""

    user_id: str
    """The ID of the user to follow."""

    type: int
    """The type of follow to perform. 1 for follow, 0 for unfollow."""

    @classmethod
    def with_user_id(cls, user_id: str, params: TikTokParams, should_follow: bool = True) -> Self:
        """Create a new FollowParams instance with the given user ID and base parameters."""
        return cls(
            **params.model_dump(by_alias=True, exclude_unset=True),
            user_id=user_id,
            type=int(should_follow),
        )
