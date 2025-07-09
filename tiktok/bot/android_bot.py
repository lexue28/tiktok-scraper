import asyncio
import json
import logging
import re
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

import cv2
import requests

# Import your agent and decision models as needed.
from tiktok.agent.agent import Agent
from tiktok.agent.models import VideoAction, VideoActions, VideoDecision
from tiktok.bot.logging_models import BotActivityLog, VideoActionLog
from tiktok.bot.prompt import get_video_prompts
from tiktok.client.tiktok_client import TikTokClient
from tiktok.models.apis.common import TikTokVideo
from tiktok.models.params.base import TikTokParams
from tiktok.models.types import AwemeId

_LOGGER = logging.getLogger(__name__)


class AndroidBotSession:
    """Tracks statistics and details for a bot session."""

    def __init__(self, session_id: str, config: dict[str, Any]) -> None:
        self.session_id = session_id
        self.start_time = datetime.now()
        self.config = config

        # stats
        self.videos_processed = 0
        self.diggs_made = 0
        self.comments_made = 0
        self.follows_made = 0

        # paths
        self.screenshots_path = Path("logs/screenshots")
        self.screenshots_path.mkdir(parents=True, exist_ok=True)

        # Setup logging directory and file.
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = (
            self.log_dir / f"bot_activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        self.activity_log = BotActivityLog(
            session_id=self.session_id,
            start_time=datetime.now(),
            cycles=[],
            total_videos=0,
            total_comments=0,
            total_diggs=0,
            config=self.config,
        )

        _LOGGER.info(
            "[Init] Initialized AndroidBotSession",
        )

    def get_screenshot_path(self, video_id: str) -> Path:
        """Generate a path for saving the video screenshot."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.screenshots_path / f"{video_id}_{timestamp}.png"

    def log_action(
        self,
        video_id: str,
        action_type: str,
        success: bool,
        details: str | None = None,
        api_response: dict[str, Any] | None = None,
    ) -> None:
        """
        Log an individual action taken by the bot.

        :param video_id: The ID of the video on which the action was taken.
        :param action_type: The type of action (e.g., NOOP, DIGG, COMMENT).
        :param success: Whether the API call for the action was successful.
        :param details: Additional details about the action, if needed.
        :param api_response: The associated API response, if any.
        """
        match action_type:
            case VideoActions.DIGG:
                self.diggs_made += 1
            case VideoActions.COMMENT:
                self.comments_made += 1
            case VideoActions.FOLLOW:
                self.follows_made += 1
            case VideoActions.LOAD:
                self.loads_made += 1

        action = VideoActionLog(
            video_id=video_id,
            action_type=action_type,
            timestamp=datetime.now(),
            success=success,
            details=details,
            api_response=api_response,
        )
        # Record the action in the current cycle.
        self.activity_log.actions.append(action)
        self.save_logs()

    def save_logs(self) -> None:
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

    def get_stats(self) -> str:
        """Get a formatted string of current session statistics."""
        duration = datetime.now() - self.start_time
        return (
            f"Session Stats:\n"
            f"Duration: {duration}\n"
            f"Videos Processed: {self.videos_processed}\n"
            f"Diggs Made: {self.diggs_made}\n"
            f"Comments Made: {self.comments_made}\n"
            f"Follows Made: {self.follows_made}"
        )


class TikTokAndroidBot:
    """
    An Android bot that uses ADB commands to interact with the running TikTok app.

    For each video, the bot:
      1. Captures a screenshot and classifies whether the content is a video or an ad/live.
      2. If it's a video, taps the share icon and then taps on the copy link option, retrieving the share link from the clipboard.
      3. Resolves the share link via an HTTP GET to extract the final URL and video ID.
      4. Uses a TikTok client to fetch video metadata.
      5. Calls an OpenAI-powered agent to decide on an action (NOOP/DIGG/COMMENT/FOLLOW).
      6. Executes the chosen action via ADB commands.
      7. Swipes to the next video.
    """

    # Define constants (you can later move these to config if needed)
    # UI Element coordinates (normalized to 0-1 range)
    # Normalized coordinates (x values divided by screen width, y values by screen height)
    SHARE_BUTTON_X = 0.9375  # 1200/1280
    SHARE_BUTTON_Y = 0.798  # 2280/2856
    LIKE_BUTTON_X = 0.9375  # 1200/1280
    LIKE_BUTTON_Y = 0.602  # 1720/2856
    COMMENT_BUTTON_X = 0.929  # 1190/1280
    COMMENT_BUTTON_Y = 0.672  # 1920/2856
    INPUT_TEXT_X = 0.2570  # 330/1280
    INPUT_TEXT_Y = 0.9454  # 2700/2856
    COPY_LINK_X = 0.25  # 320/1280
    COPY_LINK_Y = 0.8123  # 2320/2856
    POST_BUTTON_X = 0.9219  # 1180/1280
    POST_BUTTON_Y = 0.6232  # 1776/2856
    FOLLOW_BUTTON_X = 0.9297  # 1190/1280
    FOLLOW_BUTTON_Y = 0.5602  # 1600/2856

    EXIT_BUTTON_X = 0.469  # 600/1280
    EXIT_BUTTON_Y = 0.21  # 600/2856

    # Swipe coordinates to go to the next video
    SWIPE_NEXT_VIDEO_X1 = 500
    SWIPE_NEXT_VIDEO_Y1 = 900
    SWIPE_NEXT_VIDEO_X2 = 500
    SWIPE_NEXT_VIDEO_Y2 = 250

    # Add template paths as class constants
    SHARE_ICON_TEMPLATE = "assets/share_icon.png"  # You'll need to create this
    LIKE_ICON_TEMPLATE = "assets/like_icon.png"  # You'll need to create this
    COMMENT_ICON_TEMPLATE = "assets/comment_icon.png"  # You'll need to create this
    LIVE_ICON_TEMPLATE = "assets/live_icon.png"  # You'll need to create this

    def __init__(self, device: Any, agent: Agent, tiktok_client: TikTokClient) -> None:
        """
        :param device: An ADB device object (from ppadb) with the TikTok app already open.

        :param agent: An LLM-powered decision agent.

        :param tiktok_client: A TikTok client instance.
        """
        self.device = device
        self.agent = agent
        self.device_serial = device.get_serial_no()
        # Use the provided TikTokClient instance.
        self.tiktok_client = tiktok_client

        # Get device screen dimensions
        screen_size = self.device.shell("wm size").strip()
        width, height = map(int, screen_size.split()[-1].split("x"))
        self.screen_width = width
        self.screen_height = height
        _LOGGER.info(f"Device screen size: {width}x{height}")
        self.session = AndroidBotSession(
            session_id=str(uuid.uuid4()),
            config={
                "SHARE_BUTTON_X": self.SHARE_BUTTON_X,
                "SHARE_BUTTON_Y": self.SHARE_BUTTON_Y,
                "LIKE_BUTTON_X": self.LIKE_BUTTON_X,
                "LIKE_BUTTON_Y": self.LIKE_BUTTON_Y,
                "COMMENT_BUTTON_X": self.COMMENT_BUTTON_X,
                "COMMENT_BUTTON_Y": self.COMMENT_BUTTON_Y,
                "COPY_LINK_X": self.COPY_LINK_X,
                "COPY_LINK_Y": self.COPY_LINK_Y,
                "POST_BUTTON_X": self.POST_BUTTON_X,
                "POST_BUTTON_Y": self.POST_BUTTON_Y,
                "SWIPE_NEXT_VIDEO_X1": self.SWIPE_NEXT_VIDEO_X1,
                "SWIPE_NEXT_VIDEO_Y1": self.SWIPE_NEXT_VIDEO_Y1,
                "SWIPE_NEXT_VIDEO_X2": self.SWIPE_NEXT_VIDEO_X2,
                "SWIPE_NEXT_VIDEO_Y2": self.SWIPE_NEXT_VIDEO_Y2,
                "SHARE_ICON_TEMPLATE": self.SHARE_ICON_TEMPLATE,
                "LIKE_ICON_TEMPLATE": self.LIKE_ICON_TEMPLATE,
                "COMMENT_ICON_TEMPLATE": self.COMMENT_ICON_TEMPLATE,
                "LIVE_ICON_TEMPLATE": self.LIVE_ICON_TEMPLATE,
            },
        )

    async def run(self) -> None:
        """
        Main loop of the bot.

        For each video:
          - Classify the screen (video vs. ad/live).
          - Retrieve share link → resolve URL → extract video ID.
          - Retrieve video info.
          - Ask the agent to decide an action.
          - Execute the chosen action.
          - Swipe to the next video.
        """
        while True:
            screenshot_path = "/tmp/screenshot.png"
            self.capture_screenshot(screenshot_path)
            content_type, share_coords = self.classify_video_type(screenshot_path)

            if content_type != "video":
                _LOGGER.info("Content is not a video (ad/live detected). Skipping...")
                self.swipe_next_video()
                await asyncio.sleep(2)
                continue

            self.tap_on_share_icon(share_coords)
            share_link = self.get_share_link()
            if not share_link:
                _LOGGER.warning(
                    f"Failed to retrieve share link {share_link} from clipboard. Skipping video."
                )
                self.swipe_next_video()
                await asyncio.sleep(2)
                continue

            final_url = self.resolve_share_link(share_link)
            if not final_url:
                _LOGGER.warning("Failed to resolve share link. Skipping video.")
                self.swipe_next_video()
                await asyncio.sleep(2)
                continue

            video_id = self.extract_video_id(final_url)
            if not video_id:
                _LOGGER.warning("Failed to extract video id. Skipping video.")
                self.swipe_next_video()
                await asyncio.sleep(2)
                continue

            _LOGGER.info(f"Video ID extracted: {video_id}")

            # Get video info using TikTokApi (run synchronously in a thread)
            video_info = await self.get_video_info(video_id)
            if not video_info:
                _LOGGER.warning("Failed to retrieve video info. Skipping video.")
                self.swipe_next_video()
                await asyncio.sleep(2)
                continue

            prompt = get_video_prompts([video_info], list(VideoActions.__members__.keys()))
            # Pass both the prompt and screenshot to the agent
            screenshot = self.session.get_screenshot_path(video_id)
            self.capture_screenshot(str(screenshot))
            decisions = await self.agent.decide_action(
                prompt, VideoDecision, image_path=str(screenshot)
            )
            if decisions is None:
                _LOGGER.warning("No decision was returned. Skipping video.")
                self.swipe_next_video()
                await asyncio.sleep(2)
                continue

            # Should only have one action
            if len(decisions.actions) != 1:
                _LOGGER.warning(f"Expected 1 action, got {len(decisions.actions)}")
                self.swipe_next_video()
                await asyncio.sleep(2)
                continue

            # Get the first action from the dictionary
            decision = list(decisions.actions.values())[0]
            _LOGGER.info(f"Decision: {decision.action} | Reason: {decision.reason}")

            await self.perform_action(decision, video_info, screenshot_path=str(screenshot))
            self.swipe_next_video()
            await asyncio.sleep(2)

    def capture_screenshot(self, filepath: str) -> None:
        """
        Capture a screenshot of the device and save it to a file.
        """
        result = self.device.screencap()
        with open(filepath, "wb") as f:
            f.write(result)

    def classify_video_type(self, image_path: str) -> tuple[str, Sequence[int]]:
        """
        Classify content type by looking for specific UI elements using template matching.

        A regular video should have like, comment, and share buttons.
        A live stream typically won't have these interaction buttons.

        Returns a tuple of (content_type, coordinates) where coordinates are the position
        of the share button if found.

        :return: tuple[str, tuple[int, int]]: ("video", (share_x, share_y)) if share button found,
                                        ("ad/live", (0, 0)) if ad/live detected,
                                        ("unknown", (0, 0)) if nothing detected
        """
        try:
            # Read the screenshot and templates
            screen = cv2.imread(image_path)
            if screen is None:
                return "unknown", (0, 0)

            share_template = cv2.imread(self.SHARE_ICON_TEMPLATE)
            like_template = cv2.imread(self.LIKE_ICON_TEMPLATE)
            comment_template = cv2.imread(self.COMMENT_ICON_TEMPLATE)
            live_template = cv2.imread(self.LIVE_ICON_TEMPLATE)

            # Check for live indicator first
            live_result = cv2.matchTemplate(screen, live_template, cv2.TM_CCOEFF_NORMED)
            _, live_max_val, _, _ = cv2.minMaxLoc(live_result)

            if live_max_val >= 0.8:
                return "ad/live", (0, 0)

            # Look for all video interaction buttons
            share_result = cv2.matchTemplate(screen, share_template, cv2.TM_CCOEFF_NORMED)
            like_result = cv2.matchTemplate(screen, like_template, cv2.TM_CCOEFF_NORMED)
            comment_result = cv2.matchTemplate(screen, comment_template, cv2.TM_CCOEFF_NORMED)

            _, share_max_val, _, share_max_loc = cv2.minMaxLoc(share_result)
            _, like_max_val, _, _ = cv2.minMaxLoc(like_result)
            _, comment_max_val, _, _ = cv2.minMaxLoc(comment_result)

            _LOGGER.info(
                f"Button confidences: Share={share_max_val:.3f}, "
                f"Like={like_max_val:.3f}, Comment={comment_max_val:.3f}"
            )

            # If we find all interaction buttons with good confidence, it's a video
            CONFIDENCE_THRESHOLD = 0.6
            if (
                share_max_val >= CONFIDENCE_THRESHOLD
                and like_max_val >= CONFIDENCE_THRESHOLD
                and comment_max_val >= CONFIDENCE_THRESHOLD
            ):
                return "video", share_max_loc

            return "unknown", (0, 0)

        except Exception as e:
            _LOGGER.error(f"Error in classify_video_type: {e}")
            return "unknown", (0, 0)

    def get_share_link(self) -> str:
        """
        Taps the share icon, then the copy link button, and returns the share link from the clipboard.
        """
        self.tap_on_share_icon()
        time.sleep(1)
        self.tap_on_copy_link_icon()
        time.sleep(2)  # Give more time for the copy operation to complete
        link = self.get_clipboard()
        _LOGGER.info(f"Retrieved link from clipboard: {link}")
        return link

    def tap_on_share_icon(self, coords: Sequence[int] | None = None) -> None:
        """
        Tap on the share icon using preset coordinates.

        :param coords: Optional tuple of (x, y) coordinates. If not provided, uses default positions.
        """
        if coords:
            x, y = coords
            # Add offset to center of the icon
            x += 25  # Adjust based on template size
            y += 25  # Adjust based on template size
        else:
            x = int(self.screen_width * self.SHARE_BUTTON_X)
            y = int(self.screen_height * self.SHARE_BUTTON_Y)
        cmd = f"input tap {int(x)} {int(y)}"
        _LOGGER.info(f"Tapping on share icon: {cmd}")
        self.device.shell(cmd)

    def tap_on_copy_link_icon(self) -> None:
        """
        Tap on the copy link icon.

        For now, using placeholder coordinates (modify as needed).
        """
        copy_x = int(self.screen_width * self.COPY_LINK_X)
        copy_y = int(self.screen_height * self.COPY_LINK_Y)
        cmd = f"input tap {copy_x} {copy_y}"
        _LOGGER.info(f"Tapping on copy link icon: {cmd}")
        self.device.shell(cmd)

    def get_clipboard(self) -> str:
        """
        Retrieve clipboard content using Android's clipboard service.

        This method specifically looks for TikTok share URLs.
        """
        try:
            # Call clipboard service to get content
            adb_cmd = [
                "adb",
                "-s",
                self.device_serial,
                "shell",
                "service",
                "call",
                "clipboard",
                "4",
                "s16",
                "com.android.shell",
                "i32",
                "0",
            ]

            result = subprocess.run(adb_cmd, capture_output=True, text=True)
            output = result.stdout

            if not output:
                _LOGGER.warning("No output from clipboard service")
                return ""

            # Extract ASCII parts from the output
            ascii_parts = re.findall(r"'([^']*)'", output)
            if not ascii_parts:
                _LOGGER.warning("No ASCII content found in clipboard")
                return ""

            combined_output = "".join(ascii_parts)
            _LOGGER.debug(f"Combined ASCII content: {combined_output}")

            # Look specifically for TikTok share URLs
            match = re.search(r"(https://vm\.tiktok\.com/[A-Za-z0-9]+/)", combined_output)
            if match:
                _LOGGER.info(f"Found TikTok URL: {match.group(1)}")
                return match.group(1)

            _LOGGER.warning("No TikTok URL found in clipboard")
            return ""

        except Exception as e:
            _LOGGER.error(f"Error getting clipboard content: {e}")
            return ""

    def resolve_share_link(self, share_link: str) -> str:
        """
        Uses an HTTP GET (with redirects) to resolve the share link to the final URL.
        """
        try:
            response = requests.get(share_link, allow_redirects=True, timeout=10)
            return response.url
        except Exception as e:
            _LOGGER.error(f"Error resolving share link: {e}")
            return ""

    def extract_video_id(self, url: str) -> str:
        """
        Extracts the video id from the given URL.

        Assumes URLs in the format: "https://www.tiktok.com/@user/video/VIDEO_ID?...".
        """
        try:
            parts = url.split("/")
            if "video" in parts:
                index = parts.index("video")
                if index + 1 < len(parts):
                    return parts[index + 1].split("?")[0]
            return parts[-1].split("?")[0]
        except Exception as e:
            _LOGGER.error(f"Error extracting video id: {e}")
            return ""

    async def get_video_info(self, video_id: str) -> TikTokVideo | None:
        """
        Retrieves video information (synchronously) using the TikTokApi.
        """
        try:
            # Assuming the TikTokClient has a get_video_info method that takes video_id and parameters.
            info = await self.tiktok_client.get_video_details(
                AwemeId(video_id), TikTokParams.default_web()
            )
            return info.item_info.item_struct

        except Exception as e:
            _LOGGER.error(f"Error retrieving video info: {e}")
            return None

    async def perform_action(
        self,
        decision: VideoAction,
        video_info: TikTokVideo,
        screenshot_path: str | None = None,
    ) -> None:
        """
        Act on the decision returned by the agent.

        :param decision: The action decision from the agent
        :param video_info: Video metadata
        :param screenshot_path: Optional path to screenshot of current video
        """
        # Take a screenshot if one wasn't provided
        if screenshot_path is None:
            screenshot_path = "/tmp/action_screenshot.png"
            self.capture_screenshot(screenshot_path)

        success = True
        match decision.action:
            case VideoActions.NOOP:
                _LOGGER.info("No action taken.")
            case VideoActions.DIGG:
                self.tap_on_like_icon()
            case VideoActions.COMMENT:
                comment_text = await self.generate_comment(video_info)
                success = bool(comment_text)
                if success:
                    self.tap_on_comment_and_type(comment_text)
            case VideoActions.FOLLOW:
                self.tap_on_follow_icon()
            case VideoActions.LOAD:
                self.list_comments()
            case _:
                _LOGGER.warning(f"Unknown action: {decision.action}")
                success = False

        self.session.log_action(
            video_id=video_info.id,
            action_type=decision.action,
            success=success,
            details=decision.reason,
            api_response=video_info.model_dump(mode="json"),
        )
        _LOGGER.info(self.session.get_stats())

    def tap_on_like_icon(self) -> None:
        """
        Simulate a tap on the like icon.
        """
        x = int(self.screen_width * self.LIKE_BUTTON_X)
        y = int(self.screen_height * self.LIKE_BUTTON_Y)
        cmd = f"input tap {int(x)} {int(y)}"
        _LOGGER.info(f"Tapping on like icon: {cmd}")
        self.device.shell(cmd)
        time.sleep(1)

    async def generate_comment(self, video_info: TikTokVideo) -> str:
        """
        Generates a comment text by asking the agent.
        """
        try:
            comment_response = await self.agent.generate_comment(video_info.model_dump(mode="json"))
            if comment_response is None:
                return ""
            return comment_response
        except Exception as e:
            _LOGGER.error(f"Error generating comment: {e}")
            return ""

    def tap_on_comment_and_type(self, comment: str) -> None:
        """
        Tap on the comment icon, type the comment text via adb, and then submit.
        """
        comment_icon_x = int(self.screen_width * self.COMMENT_BUTTON_X)
        comment_icon_y = int(self.screen_height * self.COMMENT_BUTTON_Y)
        cmd = f"input tap {comment_icon_x} {comment_icon_y}"
        _LOGGER.info(f"Tapping on comment icon: {cmd}")
        self.device.shell(cmd)
        # Longer delay to ensure the comment icon is tapped
        time.sleep(1)

        input_text_x = int(self.screen_width * self.INPUT_TEXT_X)
        input_text_y = int(self.screen_height * self.INPUT_TEXT_Y)
        cmd = f"input tap {input_text_x} {input_text_y}"
        _LOGGER.info(f"Tapping on input text: {cmd}")
        self.device.shell(cmd)
        # Longer delay to ensure the input text is tapped
        time.sleep(1)

        # Keep only alphanumeric characters and spaces
        comment = re.sub(r"[^a-zA-Z0-9\s]", "", comment)
        # Escape text
        text = comment.replace(" ", "%s")

        cmd = f"input text {text}"
        _LOGGER.info(f"Typing comment: {cmd}")
        self.device.shell(cmd)
        # Longer delay to ensure the comment is typed
        time.sleep(3)

        # Tap the post/submit button
        post_button_x = int(self.screen_width * self.POST_BUTTON_X)
        post_button_y = int(self.screen_height * self.POST_BUTTON_Y)
        cmd = f"input tap {post_button_x} {post_button_y}"
        _LOGGER.info(f"Tapping on post button: {cmd}")
        self.device.shell(cmd)
        # Longer delay to ensure the post button is tapped
        time.sleep(1)

        exit_button_x = int(self.screen_width * self.EXIT_BUTTON_X)
        exit_button_y = int(self.screen_height * self.EXIT_BUTTON_Y)
        cmd = f"input tap {exit_button_x} {exit_button_y}"
        _LOGGER.info(f"Tapping on exit button: {cmd}")
        self.device.shell(cmd)
        time.sleep(1)

    def tap_on_follow_icon(self) -> None:
        """
        Simulate a tap on the follow icon.
        """
        follow_icon_x = int(self.screen_width * self.FOLLOW_BUTTON_X)
        follow_icon_y = int(self.screen_height * self.FOLLOW_BUTTON_Y)
        cmd = f"input tap {follow_icon_x} {follow_icon_y}"
        _LOGGER.info(f"Tapping on follow icon: {cmd}")
        self.device.shell(cmd)
        time.sleep(1)

    def swipe_next_video(self) -> None:
        """
        Swipe to the next video by simulating a swipe gesture via ADB.
        """
        # Calculate swipe coordinates based on screen dimensions
        start_x = int(self.screen_width * 0.5)  # Center of screen
        start_y = int(self.screen_height * 0.7)  # 70% down the screen
        end_x = start_x  # Same x coordinate
        end_y = int(self.screen_height * 0.3)  # 30% down the screen

        cmd = f"input swipe {start_x} {start_y} {end_x} {end_y}"
        _LOGGER.info(f"Swiping to next video: {cmd}")
        self.device.shell(cmd)
