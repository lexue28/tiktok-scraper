"""
TikTokBot: The Main Bot for TikTok Account Management.

This module defines the TikTokBot class, which is responsible for interacting with the TikTok API,
processing trending videos in cycles, and executing appropriate actions (like, comment, follow, etc.)
based on decisions from an AI agent.

Key Responsibilities:
- Fetch trending videos from TikTok.
- Split videos into batches and generate prompts for the AI agent.
- Execute AI-decided actions such as liking (digg) videos, posting comments, or following users.
- Maintain logs and cycle statistics.
- Save structured logs to a file for analysis and debugging.

The bot is designed to work in cycles and can be extended easily by modifying the agent behavior,
prompts, or adding new features.
"""

import asyncio
import json
import logging
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, SecretStr

from tiktok.agent.agent import Agent
from tiktok.agent.models import EndOfCycleActions, EndOfCycleDecision, VideoActions, VideoDecision
from tiktok.bot.config import BotConfig
from tiktok.bot.logging_models import APIResponse, BotActivityLog, CycleStats, VideoActionLog
from tiktok.bot.prompt import get_cycle_prompt, get_video_prompts
from tiktok.bot.utils import chunkize
from tiktok.client.tiktok_client import TikTokClient
from tiktok.models.apis.comment import Comment
from tiktok.models.apis.trending import TikTokVideo
from tiktok.models.params.base import TikTokParams
from tiktok.models.types import AwemeId

# Configure stdout logging
_LOGGER = logging.getLogger(__name__)


class TikTokBot:
    """
    A high-level bot that interacts with the TikTok API.

    This class manages cycles of operations, including:
      - Fetching trending videos.
      - Processing videos in batches.
      - Logging every step and storing detailed cycle statistics.
      - Executing actions such as liking (digg), commenting, or following users.

    :param ms_token: Microsoft token in a secure string format.
    :param client: An instance of the TikTok API client.
    :param agent: The AI decision-making agent.
    :param config: Configuration data for bot behavior.
    :param total_videos: Counter for total trending videos processed.
    :param total_comments: Counter for comments made.
    :param total_diggs: Counter for diggs (video likes) made.
    :param max_cycles: Maximum number of cycles to process.
    :param session_id: Unique identifier for the current session.
    :param activity_log: Log object maintaining the session's activity details.
    :param current_cycle: Statistics for the current cycle.
    :param log_dir: Directory for storing log files.
    :param log_file: Specific file path for the session's log file.
    """

    def __init__(
        self, ms_token: SecretStr, session_id: str, csrf_token: str, agent: Agent, config: BotConfig
    ):
        """
        Initialize a new TikTokBot instance.

        :param ms_token: The Microsoft token for authentication.
        :param session_id: The session identification string.
        :param csrf_token: CSRF token required for secured API calls.
        :param agent: The AI agent responsible for decision making.
        :param config: Bot configuration parameters.
        """
        # Securely store the authentication token.
        self.ms_token = ms_token

        # Create a TikTok API client instance that will handle all API operations.
        self.client = TikTokClient(
            ms_token=self.ms_token, session_id=session_id, csrf_token=csrf_token
        )

        # Store the decision-making agent.
        # self.agent = agent

        # Save bot configuration such as number of cycles and batch sizes.
        self.config = config

        # Initialize counters for overall video processing statistics.
        self.total_videos = 0
        # self.total_comments = 0
        self.total_follows = 0
        self.total_diggs = 0
        self.total_loads = 0

        # Lifecycle management
        self.max_cycles = config.max_cycles
        self.sleep_time = config.sleep_time

        # DIGGING
        self.tq_like = config.tq_like
        self.bq_like = config.bq_like

        # FOLLOWING
        self.follow = config.follow

        # READING COMMENTS
        self.comments_read = config.comments_read

        # 7.86 MIN SESSIONS
        self.session_sec = config.session_sec

        # Generate a unique session id for this run and initialize detailed logging.
        self.session_id = str(uuid.uuid4())
        self.activity_log = BotActivityLog(
            session_id=self.session_id,
            start_time=datetime.now(),
            cycles=[],
            total_videos=0,
            total_follows=0,
            total_diggs=0,
            total_loads=0,
            config=config.model_dump(),
        )
        self.current_cycle: CycleStats | None = None

        # Setup logging directory and file.
        self.log_dir = Path("logs_c3")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = (
            self.log_dir / f"bot_activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        _LOGGER.info(
            "[Init] Initialized TikTokBot with config: %s",
            config.model_dump_json(indent=2),
        )

    async def log_api_response(
        self,
        endpoint: str,
        success: bool,
        response_id: str,
        response_data: Dict[str, Any] | None = None,
        error: str | None = None,
    ) -> APIResponse | None:
        """
        Log an API response in a structured format for debugging and history.

        :param endpoint: The API endpoint that was called.
        :param success: Indicates whether the API call was successful.
        :param response_id: Unique identifier for this specific API response.
        :param response_data: Data returned from the API, if any.
        :param error: Any error details if the API call failed.

        :return: The logged API response, or None if no cycle is active.
        """
        # Only log if there is a current cycle underway.
        if self.current_cycle is None:
            return None

        api_response = APIResponse(
            id=response_id,
            endpoint=endpoint,
            timestamp=datetime.now(),
            success=success,
            response_data=response_data,
            error=error,
        )
        # Append this API response to the current cycle's log.
        self.current_cycle.api_responses.append(api_response)
        await self.save_logs()
        return api_response

    async def log_action(
        self,
        video_id: str,
        action_type: str,
        success: bool,
        api_response: APIResponse | None = None,
    ) -> None:
        """
        Log an individual action taken by the bot.

        :param video_id: The ID of the video on which the action was taken.
        :param action_type: The type of action (e.g., NOOP, DIGG, COMMENT).
        :param success: Whether the API call for the action was successful.
        :param details: Additional details about the action, if needed.
        :param api_response: The associated API response, if any.
        """
        # Skip logging if no current cycle is active.
        if self.current_cycle is None:
            return

        action = VideoActionLog(
            video_id=video_id,
            action_type=action_type,
            timestamp=datetime.now(),
            success=success,
            api_response=api_response.model_dump(mode="json") if api_response else None,
        )
        # Record the action in the current cycle.
        self.current_cycle.actions.append(action)
        await self.save_logs()

    async def save_logs(self) -> None:
        """
        Save the current state of the bot activity log to a JSON file.

        This function is called after logging API responses and actions to keep persistent logs.
        """
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                # Dump the structured log data using json.
                json.dump(self.activity_log.model_dump(), f, indent=2, default=str)
        except Exception as e:
            _LOGGER.error("Failed to save logs: %s", repr(e))

    async def run(self) -> None:
        """
        Main execution loop for the bot. The bot runs in cycles and processes trending videos.

        Each cycle performs:
          1. Fetch trending videos.
          2. Process videos in batches (defined by the configuration).
          3. For each batch, send a prompt to the AI agent and execute the returned decisions.
          4. Log actions and API responses, then decide what to do next based on the cycle completion prompt.

        The loop continues until:
          - The AI decides to quit.
          - The maximum number of cycles is reached.
        """
        cycle = 0
        while True:
            cycle += 1
            _LOGGER.info("[Cycle] Starting cycle")

            # Initialize metrics for the current cycle.
            self.current_cycle = CycleStats(
                cycle_id=cycle,
                start_time=datetime.now(),
                videos_processed=0,
                # comments_made=0,
                diggs_made=0,
                follows_made=0,
                loads_made=0,
                videos_collected=[],
                actions=[],
                api_responses=[],  # Initialize an empty list for API response logging.
            )
            # Append the current cycle log to the session activity log.
            self.activity_log.cycles.append(self.current_cycle)

            # Fetch trending videos using the client's API.
            trending_videos = await self.show_trending()
            if not trending_videos:
                _LOGGER.warning("[Trending] No trending videos retrieved")
                continue

            _LOGGER.info("[Trending] Retrieved %d trending videos", len(trending_videos))

            # Record the IDs of fetched videos into the cycle log.
            self.current_cycle.videos_collected = [video.id for video in trending_videos]
            
            # Process videos in batches using the configured batch size.
            for idx, videos in enumerate(
                chunkize(trending_videos, self.config.trending_videos_process_batch), start=1
            ):
                _LOGGER.info(
                    "[Batch] Processing batch %d/%d (%d videos)",
                    idx,
                    (len(trending_videos) + self.config.trending_videos_process_batch - 1)
                    // self.config.trending_videos_process_batch,
                    len(videos),
                )

                # Generate a prompt for the current batch of videos
                # decision_video = await self.agent.decide_action(
                #     get_video_prompts(videos, list(VideoActions.__members__.keys())), VideoDecision
                # )
                # Decide on action

                video_id = self.current_cycle.videos_collected[0]
                actions = []
                rand = random.random()
                print("rand", rand)
                success = True
                if rand < self.tq_like:
                    success = await self.digg_video(video_id)
                    self.current_cycle.diggs_made += int(success)
                    actions.append((video_id, VideoActions.DIGG))
                if rand < self.follow:
                    video = next((v for v in trending_videos if v.id == video_id), None)

                    if video is not None and video.author.id is not None:
                        success = await self.follow_user(video.author.id)
                        self.current_cycle.follows_made += int(success)
                        actions.append((video_id, VideoActions.FOLLOW))

                # load first ten comments for each
                success = await self.list_comments(video_id)
                self.current_cycle.loads_made += int(success)

                # if decision_video is None:
                #     _LOGGER.warning("[Decision] No decision made for batch %d", idx)
                #     continue
                
                # Process the decision for each video in the batch.
                # for video_id, decision in decision_video.actions.items():
                #     _LOGGER.info(
                #         "[Decision] VIDEO %s: %s, %s",
                #         video_id,
                #         decision.action,
                #         decision.reason,
                #     )
                #     video_id = self.current_cycle.videos_collected[0]
                #     print("new video id", video_id)
                #     match decision.action:
                #         case VideoActions.NOOP:
                #             pass
                #         case VideoActions.DIGG:
                #             # If the decision is DIGG, attempt to like the video.
                #             success = await self.digg_video(video_id)
                #             self.current_cycle.diggs_made += int(success)

                #         # case VideoActions.COMMENT:
                #         #     # Generate a comment for the video using the AI agent.
                #         #     comment = await self.generate_comment(video_id)

                #         #     if comment:
                #         #         # Attempt to post the generated comment.
                #         #         success = await self.post_comment(video_id, comment) is not None
                #         #         self.current_cycle.comments_made += int(success)
                #         case VideoActions.FOLLOW:
                #             # Try following the video's author if possible.
                #             video = next((v for v in trending_videos if v.id == video_id), None)

                #             if video is not None and video.author.id is not None:
                #                 success = await self.follow_user(video.author.id)
                #                 self.current_cycle.follows_made += int(success)
                #         case VideoActions.LOAD:
                #             # If the decision is load, attempt to like comments
                #             success = await self.list_comments(video_id)
                #             self.current_cycle.loads_made += int(success)
                #         case _:
                #             _LOGGER.warning("[Decision] Unknown action: %s", decision.action)

                # Update number of videos processed in the current cycle.
                self.current_cycle.videos_processed += len(videos)

                # Log the action for each video in the batch.
                for video_id, action in actions:
                    await self.log_action(
                        video_id=video_id,
                        action_type=action,
                        success=success,
                    )

                # Add a delay between batches.
                await self.sleep()

            # Mark the end time for the current cycle.
            self.current_cycle.end_time = datetime.now()

            # Update total statistics in the global activity log.
            self.activity_log.total_videos = self.total_videos
            # self.activity_log.total_comments = self.total_comments
            self.activity_log.total_follows = self.total_follows
            self.activity_log.total_diggs = self.total_diggs
            self.activity_log.total_loads = self.total_loads            


            await self.save_logs()

            _LOGGER.info(
                "[Cycle] Complete - Videos: %d, Follows: %d, Diggs: %d, Loads: %d",
                self.current_cycle.videos_processed,
                self.current_cycle.follows_made,
                self.current_cycle.diggs_made,
                self.current_cycle.loads_made,
            )

            # At the end of a cycle, decide what the next step should be:
            # continue with another cycle, search by keyword, or quit.

            # decision_cycle = await self.agent.decide_action(
            #     get_cycle_prompt(cycle, list(EndOfCycleActions.__members__.keys())),
            #     EndOfCycleDecision,
            # )

            # Execute next-cycle decision based on the agent's response.
            # match decision_cycle:
            #     case EndOfCycleActions.CONTINUE:
            #         _LOGGER.info("[Cycle] Continuing to next cycle")
            #     case EndOfCycleActions.QUIT:
            #         _LOGGER.info("[Cycle] Quitting bot operation")
            #         break
            #     case EndOfCycleActions.SEARCH:
            #         _LOGGER.info("[Cycle] Searching for specific content")
            #         continue

            # Check if the maximum number of cycles has been reached.
            if self.max_cycles is not None and cycle >= self.max_cycles:
                _LOGGER.info("[Cycle] Maximum cycles reached")
                break

    # async def generate_comment(self, video_id: str) -> str | None:
    #     """
    #     Generate a relevant comment for a given video using the AI agent.

    #     :param video_id: The identifier of the video for which to generate a comment.

    #     :return: The generated comment text, or None if generation fails.
    #     """
    #     _LOGGER.info("[Comment] Generating comment for video %s", video_id)

    #     class _Comment(BaseModel):
    #         # Nested model to parse the comment generated by the AI.
    #         comment: str

    #     try:
    #         # Create a simple prompt for comment generation.
    #         prompt = f"Generate a relevant, engaging comment for video {video_id}"
    #         comment_text = await self.agent.decide_action(prompt, _Comment)
    #         if comment_text is None:
    #             return None

    #         _LOGGER.info(
    #             "[Comment] Generated comment for video %s: %s",
    #             video_id,
    #             comment_text.comment[:50] + "..."
    #             if len(comment_text.comment) > 50
    #             else comment_text.comment,
    #         )

    #         return comment_text.comment
    #     except Exception as e:
    #         _LOGGER.error(
    #             "[Error - Comment] Failed to generate comment for video %s: %s", video_id, repr(e)
    #         )
    #         return None

    # async def post_comment(self, video_id: str, comment_text: str) -> Comment | None:
    #     """
    #     Post a generated comment on a video using the TikTok API.

    #     :param video_id: The ID of the video to comment on.
    #     :param comment_text: The comment text to post.

    #     :return: The Comment object returned by the API upon success, or None if failed.
    #     """
    #     params = TikTokParams.default_web()
    #     try:
    #         # Call the TikTok API to publish the comment.
    #         response = await self.client.publish_comment(
    #             video_id=AwemeId(video_id), comment=comment_text, params=params
    #         )
    #         # Log successful API response.
    #         await self.log_api_response(
    #             endpoint="publish_comment",
    #             success=True,
    #             response_id=f"comment_{video_id}",
    #             response_data=response.model_dump(),
    #         )
    #         _LOGGER.info("[Action] Posted comment on video %s: %s", video_id, comment_text)
    #         return response.comment
    #     except Exception as e:
    #         # Log failure details for debugging.
    #         await self.log_api_response(
    #             endpoint="publish_comment",
    #             success=False,
    #             response_id=f"comment_{video_id}",
    #             error=repr(e),
    #         )
    #         _LOGGER.error(
    #             "[Error - Comment] Error posting comment on video %s: %s", video_id, repr(e)
    #         )
    #         return None

    async def digg_video(self, video_id: str) -> bool:
        """
        Perform a "digg" (like) action on a video.

        :param video_id: Identifier of the video to like.

        :return: True if the like action was successful, False otherwise.
        """
        params = TikTokParams.default_web()
        print("video_id here", video_id)
        try:
            # Execute the like action on the provided video.
            response = await self.client.digg_video(video_id=AwemeId(video_id), params=params)
            # Log a successful API response.
            await self.log_api_response(
                endpoint="digg_video",
                success=True,
                response_id=f"digg_{video_id}",
                response_data=response.model_dump(),
            )
            _LOGGER.info("[Action] Digged video %s", video_id)
            return True
        except Exception as e:
            # Log the error details if the API call fails.
            await self.log_api_response(
                endpoint="digg_video", success=False, response_id=f"digg_{video_id}", error=repr(e)
            )
            _LOGGER.error("[Error - Digg] Error digging video %s: %s", video_id, repr(e))
            return False

    async def list_comments(self, video_id: str) -> bool:
        """
        Load comments from a video.

        :param video_id: Identifier of the video to like.

        :return: True if the load action was successful, False otherwise.
        """
        params = TikTokParams.default_web()
        try:
            # Execute the like action on the provided video.
            print("listing", AwemeId(video_id), video_id)
            response = await self.client.list_comments(video_id=AwemeId(video_id), params=params)
            # Log a successful API response.
            await self.log_api_response(
                endpoint="list_comments",
                success=True,
                response_id=f"list_comments_{video_id}",
                response_data=response.model_dump(),
            )
            _LOGGER.info("[Action] Loaded comments %s", video_id)
            return True
        except Exception as e:
            # Log the error details if the API call fails.
            await self.log_api_response(
                endpoint="list_comments", success=False, response_id=f"list_comments_{video_id}", error=repr(e)
            )
            _LOGGER.error("[Error - Digg] Error loading comments %s: %s", video_id, repr(e))
            return False
        
    async def show_trending(self) -> list[TikTokVideo]:
        """
        Fetch and return a list of trending videos from TikTok.

        :return: A list of TikTokVideo objects fetched from the trending API.
        """
        params = TikTokParams.default_web()
        # Set the number of videos to fetch per batch.
        params.count = self.config.trending_videos_fetch_batch
        # Update history length to avoid duplicates.
        params.history_len = random.randint(self.total_videos // 2, self.total_videos)
        params.vv_count_fyp = self.total_videos

        # Increment the total videos counter.
        self.total_videos += params.count

        try:
            # Call the TikTok trending API.
            response = await self.client.get_trending(params)
            # Log this API call's response.
            await self.log_api_response(
                endpoint="get_trending",
                success=True,
                response_id=f"trending_batch_{self.total_videos}",
                response_data=response.model_dump(),
            )
            return response.item_list
        except Exception as e:
            # Log any error that occurs during the API call.
            await self.log_api_response(
                endpoint="get_trending",
                success=False,
                response_id=f"trending_batch_{self.total_videos}",
                error=repr(e),
            )
            _LOGGER.error("[Error - Trending] Error fetching trending videos: %s", repr(e))
            return []

    async def follow_user(self, user_id: str) -> bool:
        """
        Follow a TikTok user based on the provided user ID.

        :param user_id: The ID of the user to follow.

        :return: True if the follow was successful (follow_status == 1), False otherwise.
        """
        params = TikTokParams.default_web()
        try:
            response = await self.client.follow_user(user_id=user_id, params=params)
            return response.follow_status == 1
        except Exception as e:
            # Log failure if unable to follow the user.
            await self.log_api_response(
                endpoint="follow_user",
                success=False,
                response_id=f"follow_{user_id}",
                error=repr(e),
            )
            _LOGGER.error("[Error - Follow] Error following user %s: %s", user_id, repr(e))
            return False

    async def sleep(self) -> None:
        """
        Sleep the bot for a random duration between 10 and 20 seconds to mimic human-like behavior.
        """
        sleep_time = random.randint(self.sleep_time[0], self.sleep_time[1])
        _LOGGER.info("[Sleep] Sleeping for %d seconds", sleep_time)
        await asyncio.sleep(sleep_time)
