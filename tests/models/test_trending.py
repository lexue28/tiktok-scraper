import tests.data as data
from tiktok.models.apis.trending import TrendingResponse


def test_trending_response() -> None:
    """Test the parsing of the trending response from data."""
    assert (
        TrendingResponse.model_validate(data.SINGLE_FYP).model_dump(
            by_alias=True, exclude_unset=True
        )
        == data.SINGLE_FYP
    )

    assert (
        TrendingResponse.model_validate(data.MULTIPLE_FYP).model_dump(
            by_alias=True, exclude_unset=True
        )
        == data.MULTIPLE_FYP
    )

    assert (
        TrendingResponse.model_validate(data.MULTIPLE_FYP_2).model_dump(
            by_alias=True, exclude_unset=True
        )
        == data.MULTIPLE_FYP_2
    )
