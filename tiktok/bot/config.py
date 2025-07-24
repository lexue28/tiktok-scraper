from pydantic_settings import BaseSettings

# from tiktok.bot.prompt import BASE_PROMPT, END_OF_CYCLE_PROMPT, VIDEO_ACTION_PROMPT

class BotConfig(BaseSettings):
    """
    Bot configuration.
    """

    # Trending videos
    trending_videos_process_batch: int = 1
    trending_videos_fetch_batch: int = 1

    max_cycles: int = 22
    sleep_time: tuple[int, int] = (10, 20)

    # base_prompt: str = BASE_PROMPT
    # video_action_prompt: str = VIDEO_ACTION_PROMPT
    # end_of_cycle_prompt: str = END_OF_CYCLE_PROMPT

    # DIGGING
    tq_like: float = 0.14
    bq_like: float = 0.06

    # FOLLOWING
    follow: float = 0.015

    # THESE ARE NOT WORKING YET
    # READING COMMENTS
    comments_read: int = 10

    # 7.86 MIN SESSIONS
    session_sec: float = 471.6
