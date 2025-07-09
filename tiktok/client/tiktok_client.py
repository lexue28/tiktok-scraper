import logging
import urllib.parse
from typing import Any, cast

import httpx
from pydantic import SecretStr

from tiktok.client.bogus import XBogus
from tiktok.client.urls import Urls, standard_headers
from tiktok.models.apis.comment import (
    CommentDiggResponse,
    CommentListResponse,
    CommentPublishResponse,
)
from tiktok.models.apis.details import VideoDetailsResponse
from tiktok.models.apis.digg import DiggResponse
from tiktok.models.apis.follow import FollowResponse
from tiktok.models.apis.search import SearchResponse
from tiktok.models.apis.trending import TrendingResponse
from tiktok.models.params.base import TikTokParams
from tiktok.models.params.comment import CommentDiggParams, CommentParams, CommentPublishParams
from tiktok.models.params.details import VideoDetailsParams
from tiktok.models.params.digg import DiggParams
from tiktok.models.params.follow import FollowParams
from tiktok.models.params.search import SearchParams
from tiktok.models.types import AwemeId

_LOGGER = logging.getLogger(__name__)


class TikTokClient:
    """Client for the TikTok API."""

    def __init__(
        self,
        ms_token: SecretStr,
        session_id: str,
        csrf_token: str,
        base_url: str = Urls.BASE_URL,
        *,
        _client: httpx.AsyncClient | None = None,
        _user_agent: str | None = None,
    ):
        self.client = _client or httpx.AsyncClient(base_url=base_url)
        self.ms_token = ms_token
        self.session_id = session_id
        self.csrf_token = csrf_token
        self.user_agent = (
            _user_agent
            or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        )

    async def _execute_request(
        self, method: str, url: str, params: dict[str, Any] | None, **kwargs: Any
    ) -> dict[str, Any]:
        """Execute a request."""
        if params is None:
            params = {}
        # Practically the authentication token
        params["msToken"] = self.ms_token.get_secret_value()

        # Sign the params
        params |= XBogus.sign(urllib.parse.urlencode(params), self.user_agent)

        headers = standard_headers(self.user_agent, self.csrf_token)
        cookies = {
            "tt_csrf_token": self.csrf_token,
            "msToken": self.ms_token.get_secret_value(),
            "sessionid": self.session_id,
        }

        response = await self.client.request(
            method, url, params=params, headers=headers, cookies=cookies, **kwargs
        )

        # TODO: TikTok responds to some failures with a 200 but empty body
        if response.text == "":
            response.status_code = 400

        response.raise_for_status()

        # Update msToken from cookies
        if "msToken" in response.cookies:
            self.ms_token = SecretStr(response.cookies["msToken"])

        return cast(dict[str, Any], response.json())

    async def get_trending(self, params: TikTokParams) -> TrendingResponse:
        """Get the trending videos."""
        _LOGGER.info(
            "[API Call] Getting trending videos -> [count: %s, vv_count_fyp: %s, from_page: %s]",
            params.count,
            params.vv_count_fyp,
            params.from_page,
        )
        response = await self._execute_request(
            method="GET",
            url=Urls.GET_TRENDING,
            params=params.model_dump(by_alias=True, exclude_unset=True),
        )

        return TrendingResponse.model_validate(response)

    async def digg_video(self, video_id: AwemeId, params: TikTokParams) -> DiggResponse:
        """Dig a video."""
        _LOGGER.info(
            "[API Call] Digging video -> [video_id: %s]",
            video_id,
        )
        digg_params = DiggParams.with_video_id(video_id, params)
        response = await self._execute_request(
            method="POST",
            url=Urls.DIGG,
            params=digg_params.model_dump(by_alias=True, exclude_unset=True),
        )
        return DiggResponse.model_validate(response)

    async def list_comments(self, video_id: AwemeId, params: TikTokParams) -> CommentListResponse:
        """List comments for a video."""
        # video_id = "7518780802759511318"
        _LOGGER.info(
            "[API Call] Listing comments -> [video_id: %s]",
            video_id,
        )
        comment_params = CommentParams.with_video_id(video_id, params)
        response = await self._execute_request(
            method="GET",
            url=Urls.GET_COMMENTS,
            params=comment_params.model_dump(by_alias=True, exclude_unset=True),
        )
        return CommentListResponse.model_validate(response)

    async def digg_comment(self, comment_id: AwemeId, params: TikTokParams) -> CommentDiggResponse:
        """Dig a comment."""
        _LOGGER.info(
            "[API Call] Digging comment -> [comment_id: %s]",
            comment_id,
        )
        digg_comment_params = CommentDiggParams.with_comment_id(comment_id, params)
        response = await self._execute_request(
            method="POST",
            url=Urls.DIGG_COMMENT,
            params=digg_comment_params.model_dump(by_alias=True, exclude_unset=True),
        )
        return CommentDiggResponse.model_validate(response)

    async def publish_comment(
        self, comment: str, video_id: AwemeId, params: TikTokParams
    ) -> CommentPublishResponse:
        """Publish a comment."""
        _LOGGER.info(
            "[API Call] Publishing comment -> [comment: %s, video_id: %s]",
            comment,
            video_id,
        )
        publish_comment_params = CommentPublishParams.with_video_id(
            comment=comment, video_id=video_id, params=params
        )
        response = await self._execute_request(
            method="POST",
            url=Urls.POST_COMMENT,
            params=publish_comment_params.model_dump(by_alias=True, exclude_unset=True),
        )
        return CommentPublishResponse.model_validate(response)

    async def search_keyword(self, keyword: str, params: TikTokParams) -> SearchResponse:
        """Search for videos."""
        _LOGGER.info(
            "[API Call] Searching -> [keyword: %s]",
            keyword,
        )
        search_params = SearchParams.with_keyword(keyword, params)
        response = await self._execute_request(
            method="GET",
            url=Urls.FULL_SEARCH,
            params=search_params.model_dump(by_alias=True, exclude_unset=True),
        )
        return SearchResponse.model_validate(response)

    async def follow_user(self, user_id: str, params: TikTokParams) -> FollowResponse:
        """Follow a user."""
        _LOGGER.info(
            "[API Call] Following user -> [user_id: %s]",
            user_id,
        )
        follow_params = FollowParams.with_user_id(user_id, params)
        response = await self._execute_request(
            method="POST",
            url=Urls.FOLLOW,
            params=follow_params.model_dump(by_alias=True, exclude_unset=True),
        )
        return FollowResponse.model_validate(response)

    async def get_video_details(
        self, video_id: AwemeId, params: TikTokParams
    ) -> VideoDetailsResponse:  # noqa: F821
        """Get the details of a video."""
        _LOGGER.info(
            "[API Call] Getting video details -> [video_id: %s]",
            video_id,
        )
        details_params = VideoDetailsParams.with_video_id(video_id, params)
        response = await self._execute_request(
            method="GET",
            url=Urls.GET_VIDEO_DETAIL,
            params=details_params.model_dump(by_alias=True, exclude_unset=True),
        )
        return VideoDetailsResponse.model_validate(response)
