# TODO[FILM]: We can probably abstract out this class based on APIs. Requirements will follow.
import asyncio
import json
import logging
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import aiofiles

from tiktok.client.tiktok_client import TikTokClient
from tiktok.models.params.base import TikTokParams

DEFAULT_OUTPUT_FOLDER = Path(__file__).parent.parent.parent / "outputs"
_LOGGER = logging.getLogger(__name__)


class CollectorState(StrEnum):
    """The collector state."""

    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class TrendingCollector:
    """A collector for trending videos from TikTok."""

    def __init__(
        self,
        client: TikTokClient,
        starting_params: TikTokParams,
        output_folder: Path = DEFAULT_OUTPUT_FOLDER,
        *,  # Helpful for testing
        _io_reader: Any = aiofiles.open,
        _test: bool = False,
    ) -> None:
        # Input params
        self.client = client
        self.params = starting_params.model_copy(deep=True)
        self.output_folder = output_folder

        # State params
        self.state = CollectorState.IDLE
        self.cycle = 0
        self.last_error: Exception | None = None

        # Dependency injection
        self._io_reader = _io_reader
        self._test = _test

    def stop(self) -> None:
        """Stop the collector."""
        self.state = CollectorState.STOPPED

    async def run(
        self,
        batch_size: int = 1,
        interval: int = 5,
        cycles: int | None = None,
        skip_exceptions: bool = False,
    ) -> str:
        """
        Run the collector for a (optionally) set number of cycles.

        This function will start collecting trending videos from TikTok APIs,
        storing the responses in an output json file.
        :param batch_size: the number of videos to pull for each iteration
        :param interval: the wait-time (in seconds) between pulls
        :param cycles: how many cycles to run. None for indefinitely.
        :param skip_exceptions: whether to skip exceptions and continue running
        :return: the output file location
        """
        _LOGGER.info(
            "Starting the collector -> [cycles: %s, batch_size: %s, interval: %s]",
            cycles,
            batch_size,
            interval,
        )

        self.state = CollectorState.RUNNING
        self.cycle = 0
        output_path = self.output_folder / "trending" / datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # While the collector is running and we haven't reached the cycle limit
        while self.state == CollectorState.RUNNING and (cycles is None or self.cycle < cycles):
            self.log_state()
            self.cycle += 1
            try:
                self.params.count = batch_size
                # scanned videos so far
                self.params.vv_count_fyp = (self.cycle - 1) * batch_size

                # Pull the trending videos
                response = await self.client.get_trending(self.params)
                await self.write_to_output(output_path, response.model_dump(mode="json"))

            except Exception as e:
                _LOGGER.exception("Error while running the collector")
                self.last_error = e

                if skip_exceptions:
                    continue

                self.state = CollectorState.ERROR
                break

            # Wait for the next cycle
            if cycles is not None and self.cycle < cycles:
                await asyncio.sleep(interval)

        return output_path.as_posix()

    async def write_to_output(self, output_path: Path, json_payload: dict[str, Any]) -> None:
        """Write json_payload to array in file."""
        # Create the output folder if it doesn't exist
        output_file = output_path / "trending.json"
        if not output_path.exists() and not self._test:
            output_path.mkdir(parents=True)

        try:
            # Append to the file if it exists
            async with self._io_reader(output_file, "r+") as f:
                content = await f.read()
                if not content:
                    await f.write(json.dumps([json_payload], indent=2))
                    return

                await f.seek(await f.tell() - 1)
                await f.write(",\n" + json.dumps(json_payload, indent=2) + "]")
        except FileNotFoundError:
            # Write to the file if it doesn't exist
            async with self._io_reader(output_file, "w") as f:
                await f.write(json.dumps([json_payload], indent=2))

    def log_state(self) -> None:
        """Log current collector state and metrics in a clear, structured format."""
        state_msg = f"Status -> [state: {self.state}, cycle: {self.cycle}, error: {str(self.last_error) if self.last_error else 'None'}]"
        self.last_error = None
        _LOGGER.info(state_msg)
