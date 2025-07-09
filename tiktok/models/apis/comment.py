from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from tiktok.models.apis.common import Extra, LogPb


class Acl(BaseModel):
    """
    Model representing ACL information in the share_info field.
    """

    code: int | None = None
    extra: str | None = None


class ShareInfo(BaseModel):
    """
    Model representing the share_info details of a comment.
    """

    acl: Acl | None = None
    desc: str | None = None
    title: str | None = None
    url: str | None = None


class SortExtraScore(BaseModel):
    """
    Model representing the extra sorting scores for a comment.
    """

    reply_score: float | None = None
    show_more_score: float | None = None


class AvatarThumb(BaseModel):
    """
    Model for a user's avatar thumbnail information.
    """

    uri: str | None = None
    url_list: list[str] | None = None
    url_prefix: str | None = None


class CommentUser(BaseModel):
    """
    Model representing a comment author's user information.
    """

    nickname: str | None = None
    sec_uid: str | None = None
    uid: str | None = None
    unique_id: str | None = None
    avatar_thumb: AvatarThumb | None = None

    accept_private_policy: bool | None = None
    account_region: str | None = None
    aweme_count: int | None = None
    comment_setting: int | None = None
    create_time: int | None = None
    custom_verify: str | None = None
    follower_count: int | None = None
    following_count: int | None = None
    is_block: bool | None = None
    is_discipline_member: bool | None = None
    language: str | None = None
    region: str | None = None
    signature: str | None = None
    status: int | None = None
    unique_id_modify_time: int | None = None
    user_mode: int | None = None
    verification_type: int | None = None
    verify_info: str | None = None


class Comment(BaseModel):
    """
    Model representing an individual comment.
    """

    author_pin: bool | None = None
    aweme_id: str | None = None
    cid: str | None = None
    collect_stat: int | None = None
    comment_language: str | None = None
    comment_post_item_ids: list[Any] | None = None
    create_time: int | None = None
    digg_count: int | None = None
    forbid_reply_with_video: bool | None = None
    image_list: list[Any] | None = None
    is_author_digged: bool | None = None
    is_comment_translatable: bool | None = None
    label_list: list[Any] | None = None
    no_show: bool | None = None
    reply_comment: list[Any] | None = None
    reply_comment_total: int | None = None
    reply_id: str | None = None
    reply_to_reply_id: str | None = None
    share_info: ShareInfo | None = None
    sort_extra_score: SortExtraScore | None = None
    sort_tags: str | None = None
    status: int | None = None
    stick_position: int | None = None
    text: str | None = None
    text_extra: list[Any] | None = None
    trans_btn_style: int | None = None
    user: CommentUser | None = None
    user_buried: bool | None = None
    user_digged: int | None = None


class CommentListResponse(BaseModel):
    """
    Response model for a comment list endpoint.

    Example JSON structure:
    {
        "alias_comment_deleted": false,
        "comments": [ ... ],
        "cursor": 20,
        "extra": {
            "api_debug_info": null,
            "fatal_item_ids": null,
            "now": 1739105792000
        },
        "has_filtered_comments": 0,
        "has_more": 1,
        "log_pb": {
            "impr_id": "202502091256312E7B71732B090565C6AF"
        },
        "reply_style": 2,
        "status_code": 0,
        "status_msg": "",
        "top_gifts": null,
        "total": 252
    }
    """

    alias_comment_deleted: bool | None = None
    comments: list[Comment] = Field(default_factory=list)
    cursor: int | None = None
    extra: Extra | None = None
    has_filtered_comments: int | None = None
    has_more: bool | None = None
    log_pb: LogPb | None = None
    reply_style: int | None = None
    status_code: int | None = None
    status_msg: str | None = None
    top_gifts: Any | None = None
    total: int | None = None


class CommentDiggResponse(BaseModel):
    """
    Response model for the trending feed endpoint.

    Example top-level JSON structure includes:
    ```json
    {
      "item_list": [...],
      "extra": { ... },
      "has_more": true,
      "statusCode": 0,
      "status_code": 0,
      "status_msg": "",
      "log_pb": { ... }
    }
    ```
    """

    model_config = ConfigDict(populate_by_name=True)

    extra: Extra | None = None
    """Additional metadata about the response, see `Extra` model."""

    status_code: int | None = None
    """API response status code (0 indicates success). 
    The sample JSON has both `statusCode` and `status_code` fields as `0`."""

    status_msg: str | None = None
    """Status message accompanying the response, often an empty string `""`."""

    log_pb: LogPb | None = None
    """Protocol buffer logging data, see `LogPb` model."""


class CommentPublishResponse(CommentDiggResponse):
    """
    Response model for the comment publish endpoint.
    """

    comment: Comment
    label_info: str
