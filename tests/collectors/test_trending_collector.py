import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

import tests.data as data
from tests.mock import FakeIOReader
from tiktok.client.tiktok_client import TikTokClient
from tiktok.collectors.trending import CollectorState, TrendingCollector
from tiktok.models.apis.trending import TrendingResponse
from tiktok.models.params.base import TikTokParams


@pytest.fixture
def collector(
    tiktok_client: TikTokClient, tmp_path: Path, io_reader: FakeIOReader
) -> TrendingCollector:
    params = TikTokParams.default_web()
    return TrendingCollector(tiktok_client, params, tmp_path, _io_reader=io_reader, _test=True)


async def test_run_collector(tiktok_client: Mock, collector: TrendingCollector) -> None:
    tiktok_client.get_trending = AsyncMock(
        return_value=TrendingResponse.model_validate(data.SINGLE_FYP)
    )

    await collector.run(cycles=1, interval=0)

    assert collector.state == CollectorState.RUNNING
    assert collector.cycle == 1
    tiktok_client.get_trending.assert_called_once()


async def test_run_collector_with_error(tiktok_client: Mock, collector: TrendingCollector) -> None:
    tiktok_client.get_trending.side_effect = Exception("Test error")

    await collector.run(cycles=1)

    assert collector.state == CollectorState.ERROR
    assert collector.last_error is not None


async def test_write_to_output(collector: TrendingCollector) -> None:
    json_payload = {"test": "data"}
    output_path = Path("/test")

    await collector.write_to_output(output_path, json_payload)

    expected = json.dumps([json_payload], indent=2)
    assert collector._io_reader.files[str(output_path / "trending.json")].content == expected


async def test_write_to_output_appends(collector: TrendingCollector) -> None:
    output_path = Path("/test")
    first_payload = {"test": "first"}
    second_payload = {"test": "second"}

    await collector.write_to_output(output_path, first_payload)
    await collector.write_to_output(output_path, second_payload)

    file_content = collector._io_reader.files[str(output_path / "trending.json")].content
    print(file_content)
    data = json.loads(file_content)
    assert len(data) == 2
    assert data[0] == first_payload
    assert data[1] == second_payload


def test_stop_collector(collector: TrendingCollector) -> None:
    collector.stop()
    assert collector.state == CollectorState.STOPPED
