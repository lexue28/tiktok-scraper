from pydantic import BaseModel, ConfigDict, Field

from tiktok.models.apis.common import Extra, LogPb, TikTokVideo


class VideoInfo(BaseModel):
    """The video details."""

    item_struct: TikTokVideo = Field(alias="itemStruct")
    """The video details."""


class VideoDetailsResponse(BaseModel):
    """
    Response model for the video details endpoint.

    Example top-level JSON structure includes:
    ```json
    {
      "itemInfo": [...],
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

    item_info: VideoInfo = Field(alias="itemInfo")
    """The video details. See `TikTokVideo` model."""

    extra: Extra
    """Additional metadata about the response, see `Extra` model."""

    statusCode: int
    status_code: int
    """API response status code (0 indicates success). 
    The sample JSON has both `statusCode` and `status_code` fields as `0`."""

    status_msg: str
    """Status message accompanying the response, often an empty string `""`."""

    log_pb: LogPb
    """Protocol buffer logging data, see `LogPb` model."""
