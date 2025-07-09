import httpx
import pytest

from tests.mock import FakeIOReader, create_mock
from tiktok.client.tiktok_client import TikTokClient


@pytest.fixture
def client() -> httpx.AsyncClient:
    return create_mock(httpx.AsyncClient)


@pytest.fixture
def tiktok_client() -> TikTokClient:
    return create_mock(TikTokClient)


@pytest.fixture
def io_reader() -> FakeIOReader:
    return FakeIOReader({})
