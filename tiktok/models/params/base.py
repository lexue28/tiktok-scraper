from typing import Self

from pydantic import BaseModel, Field


class TikTokParams(BaseModel):
    """Parameters for the TikTok trending/recommended items endpoint."""

    # Device & Browser Information
    device_id: str | None = None
    """Unique ID for the user's device."""
    device_platform: str | None = None
    """Indicates this is a web-based request."""
    device_type: str | None = None
    """Indicates the type of device and video encoding format."""
    browser_name: str | None = None
    """Browser name."""
    browser_platform: str | None = None
    """Platform (e.g., MacOS)."""
    browser_version: str | None = None
    """Details about the browser version."""
    browser_online: str | None = None
    """Browser online status."""
    os: str | None = None
    """Operating system."""
    screen_height: int | None = None
    """Screen height in pixels."""
    screen_width: int | None = None
    """Screen width in pixels."""

    # App & Language Settings
    aid: str | None = None
    """App ID, identifying this as a request from TikTok's web platform."""
    app_name: str | None = None
    """Application name indicating web platform."""
    app_language: str | None = None
    """Application language setting."""
    browser_language: str | None = None
    """Browser language setting."""
    language: str | None = None
    """Interface language preference."""
    webcast_language: str | None = None
    """Webcast language setting."""

    # User Context & State
    web_id_last_time: int | None = Field(None, serialization_alias="WebIdLastTime")
    """Session or user-related identifier for last web access time."""
    focus_state: str | None = None
    """Window focus state."""
    is_fullscreen: str | None = None
    """Fullscreen status."""
    is_page_visible: str | None = None
    """Page visibility status."""
    cookie_enabled: str | None = None
    """Cookie status in browser."""
    history_len: int
    """User's browsing history length within session."""

    # Content & Feed Parameters
    from_page: str
    """Source page (e.g., For You Page)."""
    count: int
    """Number of items to return."""
    pull_type: int | None = Field(None, serialization_alias="pullType")
    """Type of content pull request."""
    item_id: str | None = Field(None, serialization_alias="itemID")
    """Item identifier."""
    is_non_personalized: str | None = Field(None, serialization_alias="isNonPersonalized")
    """Non-personalized feed flag."""
    vv_count_fyp: int | None = None
    """For You Page view count."""

    # Region & Localization
    region: str | None = None
    """Region code."""
    priority_region: str | None = None
    """Priority region code."""
    tz_name: str | None = None
    """Timezone name."""

    # Tracking & Features
    data_collection_enabled: str | None = None
    """Data collection status."""
    show_about_this_ad: str | None = Field(None, serialization_alias="showAboutThisAd")
    """Show about this ad flag."""
    show_ads: str | None = Field(None, serialization_alias="showAds")
    """Show ads flag."""
    client_ab_versions: str | None = Field(None, serialization_alias="clientABVersions")
    """Client A/B testing versions."""

    # Authentication & Security
    user_is_login: str | None = None
    """User login status."""
    odin_id: str | None = Field(None, serialization_alias="odinId")
    """ODIN identifier."""
    verify_fp: str | None = None
    """Verification fingerprint."""
    ms_token: str | None = Field(None, serialization_alias="msToken")
    """MS security token."""
    x_bogus: str | None = Field(None, serialization_alias="X-Bogus")
    """X-Bogus security token."""
    signature: str | None = Field(None, serialization_alias="_signature")
    """Request signature."""

    # Other
    cover_format: int | None = Field(None, serialization_alias="coverFormat")
    """Cover format version."""
    referer: str | None = None
    """Referrer URL."""
    channel: str | None = None
    """Distribution channel."""
    watch_live_last_time: str | None = Field(None, serialization_alias="watchLiveLastTime")
    """Last live watch timestamp."""

    app_version: str | None = None
    """Application version code derived from the query parameters."""

    effect_sdk_version: str | None = None
    """Effect SDK version derived from the query parameters."""

    last_install_time: int | None = None
    """Time of the last installation, derived from the 'last_install_time' query param."""

    is_pad: str | None = None
    """Indicates if the device is a tablet, derived from 'is_pad' (0 or 1)."""

    @classmethod
    def default_web(cls) -> Self:
        """Create a default set of parameters for a web-based request."""
        return cls(
            aid="1988",
            app_language="en",
            app_name="tiktok_web",
            browser_language="en-US",
            browser_name="Mozilla",
            browser_online="true",
            browser_platform="MacIntel",
            browser_version="5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            channel="tiktok_web",
            cookie_enabled="true",
            count=10,
            device_id="7433893465412503072",
            device_platform="web_pc",
            focus_state="true",
            from_page="fyp",
            history_len=100,
            is_fullscreen="true",
            is_page_visible="true",
            language="en",
            os="mac",
            priority_region="",
            referer="",
            region="IT",
            screen_height=982,
            screen_width=1512,
            tz_name="Europe/Rome",
            webcast_language="en",
        )

    @classmethod
    def default_android(cls) -> Self:
        """Create a default set of parameters for an Android-based request."""
        return cls(
            # Derived from query params & common-params-v2 header
            device_platform="android",
            os="android",
            app_name="musical_ly",
            aid="1988",
            app_language="en",
            browser_language="en-US",
            browser_name="com.zhiliaoapp.musically/2023700040 (Android 15)",
            browser_online="true",
            browser_platform="Android",
            browser_version="37.0.4",
            webcast_language="en",
            priority_region="",
            language="en",
            region="US",
            screen_width=1440,
            screen_height=3120,
            channel="googleplay",
            device_type="sdk_gphone64_arm64",
            device_id="7464203107687286318",
            pull_type=2,
            is_non_personalized="0",
            last_install_time=1737895300,
            effect_sdk_version="17.6.0",
            app_version="2023700040",
            is_pad="0",
            tz_name="Europe/Rome",
            cookie_enabled="true",
            focus_state="true",
            from_page="fyp",
            history_len=100,
            is_fullscreen="true",
            is_page_visible="true",
            count=10,
        )
