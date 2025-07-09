import logging
import sys
from typing import Final

import colorlog

_LOGGER = logging.getLogger(__name__)

KNOWN_SPAMMY_LOGGERS: Final[dict[str, int]] = {
    "aiohttp.client": logging.ERROR,
    "hpack": logging.WARNING,
    "httpx": logging.WARNING,
    "kubernetes_asyncio.client": logging.INFO,
    "google.ads.googleads.client": logging.ERROR,
    "google.api_core.bidi": logging.WARNING,
    "google.cloud.pubsub_v1.subscriber": logging.WARNING,
    "PIL": logging.WARNING,
    "slack_sdk": logging.WARNING,
    "slack.web": logging.WARNING,
    "urllib3.connectionpool": logging.WARNING,
}
"""
Known spammy loggers among several projects.

NOTE: We expose this sequence so that people can leverage it and easily extend it if needed. We also
 encourage you to add more to it directly here in the library if you feel it appropriate.
"""


def _set_up_local(log_level: int) -> None:
    """
    Set up the local logging.

    :param log_level: minimum severity to be logged
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    handler: logging.Handler = colorlog.StreamHandler(sys.stdout)
    handler.setFormatter(
        colorlog.ColoredFormatter(
            fmt=(
                "[%(asctime)s.%(msecs)03d] "
                "%(log_color)s%(levelname)-5s %(name)-27s %(reset)s| "
                "%(message)s"
            ),
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "green",
                "INFO": "blue",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )
    root_logger.addHandler(handler)


def set_up(log_level: int = logging.INFO) -> None:
    """Set up logging."""
    _set_up_local(log_level=log_level)

    for logger_name, logger_level in (KNOWN_SPAMMY_LOGGERS).items():
        logging.getLogger(logger_name).setLevel(logger_level)
