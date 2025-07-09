from unittest.mock import ANY, AsyncMock, Mock

import httpx
import pytest
from pydantic import SecretStr

import tests.data as data
from tiktok.client.tiktok_client import TikTokClient
from tiktok.client.urls import Urls
from tiktok.models.params.base import TikTokParams
from tiktok.models.types import AwemeId

MS_TOKEN = "test_token"


@pytest.fixture
def tiktok_client(client: httpx.AsyncClient) -> TikTokClient:
    return TikTokClient(
        base_url="https://www.test-tiktok.com",
        ms_token=SecretStr(MS_TOKEN),
        _client=client,
        session_id="test_session_id",
        csrf_token="test_csrf_token",
    )


async def test_trending(client: Mock, tiktok_client: TikTokClient) -> None:
    """Test the get_trending method."""
    params = TikTokParams.default_web()
    params.ms_token = MS_TOKEN

    mock_response = httpx.Response(
        200,
        json=data.SINGLE_FYP,
        request=Mock(headers={}, url="https://www.example.com/"),
    )
    client.request = AsyncMock(return_value=mock_response)

    await tiktok_client.get_trending(params)

    client.request.assert_called_once_with(
        "GET",
        Urls.GET_TRENDING,
        params={
            "X-Bogus": ANY,
            **params.model_dump(by_alias=True, exclude_unset=True),
        },
        headers=ANY,
        cookies=ANY,
    )


async def test_digg(client: Mock, tiktok_client: TikTokClient) -> None:
    """Test the digg method."""
    params = TikTokParams.default_web()
    params.ms_token = MS_TOKEN
    video_id = AwemeId("1234567890")

    mock_response = httpx.Response(
        200,
        json=data.DIGG_RESPONSE,
        request=Mock(headers={}, url="https://www.test-tiktok.com/api/v1/aweme/digg/"),
    )
    client.request = AsyncMock(return_value=mock_response)

    await tiktok_client.digg_video(video_id, params)

    client.request.assert_called_once_with(
        "POST",
        Urls.DIGG,
        params={
            "aweme_id": video_id,
            "type": 1,
            "X-Bogus": ANY,
            **params.model_dump(by_alias=True, exclude_unset=True),
        },
        headers=ANY,
        cookies=ANY,
    )


async def test_search_users(client: Mock, tiktok_client: TikTokClient) -> None:
    """Test the search_users method."""
    params = TikTokParams.default_web()
    params.ms_token = MS_TOKEN
    keyword = "test"

    mock_response = httpx.Response(
        200,
        json=data.SEARCH_RESPONSE,
        request=Mock(headers={}, url="https://www.test-tiktok.com/"),
    )
    client.request = AsyncMock(return_value=mock_response)

    await tiktok_client.search_keyword(keyword, params)

    client.request.assert_called_once_with(
        "GET",
        Urls.FULL_SEARCH,
        params={
            "keyword": keyword,
            "X-Bogus": ANY,
            **params.model_dump(by_alias=True, exclude_unset=True),
        },
        headers=ANY,
        cookies=ANY,
    )


async def test_comment_digg(client: Mock, tiktok_client: TikTokClient) -> None:
    """Test the comment_digg method."""
    params = TikTokParams.default_web()
    params.ms_token = MS_TOKEN
    comment_id = AwemeId("1234567890")

    mock_response = httpx.Response(
        200,
        json=data.COMMENT_DIGG_RESPONSE,
        request=Mock(headers={}, url="https://www.test-tiktok.com/api/v1/comment/digg/"),
    )
    client.request = AsyncMock(return_value=mock_response)

    await tiktok_client.digg_comment(comment_id, params)

    client.request.assert_called_once_with(
        "POST",
        Urls.DIGG_COMMENT,
        params={
            "cid": comment_id,
            "digg_type": 1,
            "X-Bogus": ANY,
            **params.model_dump(by_alias=True, exclude_unset=True),
        },
        headers=ANY,
        cookies=ANY,
    )


async def test_publish_comment(client: Mock, tiktok_client: TikTokClient) -> None:
    """Test the publish_comment method."""
    params = TikTokParams.default_web()
    params.ms_token = MS_TOKEN
    video_id = AwemeId("1234567890")
    text = "test comment"

    mock_response = httpx.Response(
        200,
        json=data.COMMENT_PUBLISH_RESPONSE,
        request=Mock(headers={}, url="https://www.test-tiktok.com/api/v1/comment/publish/"),
    )
    client.request = AsyncMock(return_value=mock_response)

    await tiktok_client.publish_comment(comment=text, video_id=video_id, params=params)

    client.request.assert_called_once_with(
        "POST",
        Urls.POST_COMMENT,
        params={
            "aweme_id": video_id,
            "text": text,
            "X-Bogus": ANY,
            **params.model_dump(by_alias=True, exclude_unset=True),
        },
        headers=ANY,
        cookies=ANY,
    )

async def test_list_comments(client: Mock, tiktok_client: TikTokClient) -> None:
    """Test the list comments method."""
    params = TikTokParams.default_web()
    params.ms_token = MS_TOKEN
    video_id = AwemeId("1234567890")


    mock_response = httpx.Response(
        200,
        json=data.LIST_COMMENTS_RESPONSE,
        request=Mock(headers={}, url="https://www.example.com/"),
    )
    client.request = AsyncMock(return_value=mock_response)

    await tiktok_client.list_comments(video_id, params)

    client.request.assert_called_once_with(
        "GET",
        Urls.GET_COMMENTS,
        params={
            "aweme_id": video_id,
            "X-Bogus": ANY,
            **params.model_dump(by_alias=True, exclude_unset=True),
        },
        headers=ANY,
        cookies=ANY,
    )