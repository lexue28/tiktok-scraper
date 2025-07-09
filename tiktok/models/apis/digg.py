from pydantic import BaseModel, ConfigDict

from tiktok.models.apis.common import Extra, LogPb


class DiggResponse(BaseModel):
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

    is_digg: int | None = None
    """Indicates if the video was digged, 1 if it was, 0 if it was not."""

    status_code: int | None = None
    """API response status code (0 indicates success). 
    The sample JSON has both `statusCode` and `status_code` fields as `0`."""

    status_msg: str | None = None
    """Status message accompanying the response, often an empty string `""`."""

    log_pb: LogPb | None = None
    """Protocol buffer logging data, see `LogPb` model."""
