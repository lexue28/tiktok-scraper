from pydantic import BaseModel, ConfigDict, Field

from tiktok.models.apis.common import Extra, LogPb, TikTokVideo


class TrendingResponse(BaseModel):
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

    item_list: list[TikTokVideo] = Field(alias="itemList")
    """List of trending TikTok videos. Each item is a `TikTokVideo`."""

    extra: Extra
    """Additional metadata about the response, see `Extra` model."""

    has_more: bool = Field(alias="hasMore")
    """Indicates if more items are available for pagination, e.g. `true`."""

    statusCode: int
    status_code: int
    """API response status code (0 indicates success). 
    The sample JSON has both `statusCode` and `status_code` fields as `0`."""

    status_msg: str
    """Status message accompanying the response, often an empty string `""`."""

    log_pb: LogPb
    """Protocol buffer logging data, see `LogPb` model."""


class SimulateWatchResponse(BaseModel):
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
