from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Configuration for the TikTok bot.
    """

    ms_token: SecretStr | None = None
    session_id: str | None = None
    csrf_token: str | None = None
    openai_api_key: SecretStr | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"
