from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """Record of an API response."""

    id: str  # Structured ID like "get_trending_batch_1" or "comment_7189457812"
    endpoint: str
    timestamp: datetime
    success: bool
    response_data: dict[str, Any] | None = None
    error: str | None = None


class VideoActionLog(BaseModel):
    """Record of an action taken on a video."""

    video_id: str
    action_type: str
    timestamp: datetime
    success: bool
    details: str | None = None
    api_response: dict[str, Any] | None = None


class CycleStats(BaseModel):
    """Statistics for a single cycle."""

    cycle_id: int
    start_time: datetime
    end_time: datetime | None = None
    videos_processed: int
    # comments_made: int
    diggs_made: int
    follows_made: int
    loads_made: int
    videos_collected: list[str]
    videos_watched: list[str]
    actions: list[VideoActionLog]
    api_responses: list[APIResponse]


class BotActivityLog(BaseModel):
    """Complete log of bot activity."""

    session_id: str
    start_time: datetime
    cycles: list[CycleStats] = Field(default_factory=list)
    actions: list[VideoActionLog] = Field(default_factory=list)
    total_videos: int
    total_follows: int
    total_diggs: int
    total_loads: int
    config: dict[str, Any]

class VideoActions(StrEnum):
    """
    A decision about what action to take.
    """
    DIGG = "digg"
    FOLLOW = "follow"
