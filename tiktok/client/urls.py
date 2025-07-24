from enum import StrEnum


class Urls(StrEnum):
    """Urls for Tik:k API."""

    BASE_URL = "https://www.tiktok.com"

    # Trending
    GET_TRENDING = "/api/recommend/item_list/"

    # Digg
    DIGG = "/api/commit/item/digg/"

    # Comment
    GET_COMMENTS = "/api/comment/list/"
    DIGG_COMMENT = "/api/comment/digg/"
    # POST_COMMENT = "/api/comment/publish/"

    # Search
    FULL_SEARCH = "/api/search/general/full/"

    # Follow
    FOLLOW = "/api/commit/follow/user/"

    # Video
    GET_VIDEO_DETAIL = "/api/item/detail/"


def standard_headers(user_agent: str, tt_csrf_token: str) -> dict[str, str]:
    """Standard headers for Tik:k API."""
    return {
        "content-length": "0",
        "user-agent": user_agent,
        "content-type": "application/x-www-form-urlencoded",
        "accept": "*/*",
        "origin": "https://www.tiktok.com",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.tiktok.com/",
        "accept-language": "en-US,en;q=0.9",
        "tt-csrf-token": tt_csrf_token,
    }
