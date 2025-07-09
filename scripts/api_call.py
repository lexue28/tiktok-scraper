import asyncio

from pydantic import SecretStr

from tiktok.client.tiktok_client import TikTokClient
from tiktok.models.params.base import TikTokParams
from tiktok.models.types import AwemeId

BASE_URL = "https://www.tiktok.com"
MS_TOKEN = "<ms_token>"
SESSION_ID = "<session_id>"
CSRF_TOKEN = "<csrf_token>"


async def api_call() -> None:
    """Test an API call locally."""
    client = TikTokClient(
        base_url=BASE_URL,
        ms_token=SecretStr(MS_TOKEN),
        session_id=SESSION_ID,
        csrf_token=CSRF_TOKEN,
    )

    params = TikTokParams.default_web()
    params.count = 1

    # print("Getting Trendings...")
    # trendings = await client.get_trending(params=params)
    # video_id = AwemeId(trendings.item_list[0].id)
    # print("Video ID: ", video_id)
    # await asyncio.sleep(2)

    # print("Digging Video...")
    # digg_video = await client.digg_video(video_id=video_id, params=params)
    # print("Digg Video: ", digg_video.model_dump_json(indent=2))
    # await asyncio.sleep(2)

    # print("Getting Comments...")
    # comments = await client.list_comments(video_id=video_id, params=params)
    # print("Comments: ", comments.model_dump_json(indent=2))
    # comment_id = AwemeId(comments.comments[0].cid or "")
    # await asyncio.sleep(2)

    # print("Digging Comment...")
    # digg_comment = await client.digg_comment(comment_id=comment_id, params=params)
    # print("Digg Comment: ", digg_comment.model_dump_json(indent=2))
    # await asyncio.sleep(2)

    # print("Publishing Comment...")
    # publish_comment = await client.publish_comment(
    #     comment="Hello, world!", video_id=video_id, params=params
    # )
    # print("Publish Comment: ", publish_comment.model_dump_json(indent=2))
    # await asyncio.sleep(2)

    # print("Getting Comments After Publish...")
    # comments_after_publish = await client.list_comments(video_id=video_id, params=params)
    # print("Comments After Publish: ", comments_after_publish.model_dump_json(indent=2))
    # await asyncio.sleep(2)

    # print("Searching Keyword...")
    # search_response = await client.search_keyword(keyword="donald trump", params=params)
    # print("Search Response: ", search_response.model_dump_json(indent=2))
    # await asyncio.sleep(2)

    video_id = AwemeId("7470238360603200814")
    print("Getting Video Details...")
    video_details = await client.get_video_details(video_id=video_id, params=params)
    print("Video Details: ", video_details.model_dump_json(indent=2))
    await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(api_call())
