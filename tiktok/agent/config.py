from pydantic_settings import BaseSettings

class AgentConfig(BaseSettings):
    """
    agent configuration.
    """
    # DIGGING
    tq_like: float = 0.14
    bq_like: float = 0.06

    # FOLLOWING
    follow: float = 0.015

    # READING COMMENTS (to feed to llm)
    load: float = 1
    comments_read: int = 10

    # 7.86 MIN SESSIONS
    session_sec: float = 471.6