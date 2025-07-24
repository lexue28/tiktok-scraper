import asyncio
import logging

import questionary
from openai import OpenAI
from ppadb.client import Client as AdbClient
from pydantic import SecretStr

from tiktok import log
from tiktok.bot.config import BotConfig
from tiktok.bot.tiktok_bot import TikTokBot
from tiktok.client.tiktok_client import TikTokClient
from tiktok.config import Config

_LOGGER = logging.getLogger(__name__)


async def web_main() -> None:
    """Main function."""
    # Attempt to load values from the .env file using our Config
    config = Config()
    bot_config = BotConfig()

    # Get required tokens and keys
    ms_token = (
        config.ms_token.get_secret_value()
        if config.ms_token is not None
        else await questionary.password("Enter your ms_token:").ask_async()
    )
    session_id = (
        config.session_id
        if config.session_id is not None
        else await questionary.text("Enter your session_id:").ask_async()
    )
    csrf_token = (
        config.csrf_token
        if config.csrf_token is not None
        else await questionary.password("Enter your csrf_token:").ask_async()
    )

    # Instantiate the Agent with the OpenAI client, base prompt, and behavior context

    # Create and run the TikTok bot
    bot = TikTokBot(
        ms_token=SecretStr(ms_token),
        session_id=session_id,
        csrf_token=csrf_token,
        config=bot_config,
    )

    try:
        await bot.run()
    except KeyboardInterrupt:
        _LOGGER.info("Bot stopped by user")
    except Exception as e:
        _LOGGER.error("Bot stopped due to error: %s", repr(e))
    # finally:
    #     await agent.close()


# async def android_main() -> None:
#     """Android bot main function."""
#     # Attempt to load values from the .env file using our Config
#     config = Config()

#     # Get required tokens and keys
#     ms_token = (
#         config.ms_token.get_secret_value()
#         if config.ms_token is not None
#         else await questionary.password("Enter your ms_token:").ask_async()
#     )
#     session_id = (
#         config.session_id
#         if config.session_id is not None
#         else await questionary.text("Enter your session_id:").ask_async()
#     )
#     csrf_token = (
#         config.csrf_token
#         if config.csrf_token is not None
#         else await questionary.password("Enter your csrf_token:").ask_async()
#     )
#     openai_key = (
#         config.openai_api_key.get_secret_value()
#         if config.openai_api_key is not None
#         else await questionary.password("Enter your OpenAI API key:").ask_async()
#     )

#     # Define base prompt and behavior context for the agent
#     base_prompt = """You are an AI assistant that helps interact with TikTok videos.
# Your role is to analyze videos and decide appropriate actions like commenting or liking.
# You should make decisions that help create engaging and positive interactions.
# {behavior_context}"""

#     # Define the behavior context that guides the agent's personality
#     behavior_context = prompt.TRUMP_PROMPT

#     # Create an OpenAI client instance
#     openai_client = OpenAI(api_key=openai_key)

#     # Instantiate the Agent with the OpenAI client, base prompt, and behavior context
#     agent = Agent(openai_client, base_prompt, behavior_context)

#     # Connect to ADB and get device
#     adb_client = AdbClient(host="127.0.0.1", port=5037)
#     devices = adb_client.devices()
#     if devices:
#         device = devices[0]
#         _LOGGER.info(f"Using device: {device.get_serial_no()}")
#     else:
#         # Prompt for the ADB device name (or default to the first connected device)
#         device_name = await questionary.text(
#             "Enter your ADB device name (leave empty to use first detected device):"
#         ).ask_async()

#         if device_name:
#             device = adb_client.device(device_name)
#             if not device:
#                 _LOGGER.error(f"Device {device_name} not found!")
#                 return

#     # Create TikTok client for API operations
#     tiktok_client = TikTokClient(
#         ms_token=SecretStr(ms_token),
#         session_id=session_id,
#         csrf_token=csrf_token,
#     )

#     # Create and initialize the Android bot
#     bot = TikTokAndroidBot(
#         device=device,
#         agent=agent,
#         tiktok_client=tiktok_client,
#     )

#     try:
#         await bot.run()
#     except KeyboardInterrupt:
#         _LOGGER.info("Bot stopped by user")
#     except Exception as e:
#         _LOGGER.error("Bot stopped due to error: %s", repr(e))
#         raise
#     finally:
#         await agent.close()


if __name__ == "__main__":
    log.set_up()
    # Choose which bot to run
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--android":
        asyncio.run(android_main())
    else:
        asyncio.run(web_main())
