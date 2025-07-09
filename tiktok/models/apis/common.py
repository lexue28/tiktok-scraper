from typing import Any, Optional

from pydantic import BaseModel, Field

from tiktok.models.common import CamelizeBaseModel, PascalizeBaseModel


class Extra(CamelizeBaseModel):
    """
    Metadata about the API response.

    Example JSON snippet from 'extra':
    ```json
    "extra": {
      "fatal_item_ids": [],
      "logid": "202501121902273982D6E9DE7DB214C226",
      "now": 1736708547000
    }
    ```
    """

    # fatal_item_ids: list[str] = Field(default_factory=list, alias="fatal_item_ids")
    fatal_item_ids: Optional[list[str]] = Field(default_factory=list, alias="fatal_item_ids")

    """List of IDs that caused fatal errors during processing

    In the example JSON, this appears as `"fatal_item_ids": []`.
    """

    logid: str | None = None
    """Unique identifier for the API request log

    For instance, `"logid": "202501121902273982D6E9DE7DB214C226"` in the example.
    """

    now: int | None = None
    """Current timestamp in milliseconds

    For example, `"now": 1736708547000`.
    """


class LogPb(BaseModel):
    """
    Protocol buffer logging information.

    Example snippet from 'log_pb':
    ```json
    "log_pb": {
      "impr_id": "202501121902273982D6E9DE7DB214C226"
    }
    ```
    """

    impr_id: str | None = None
    """Impression ID for analytics tracking

    Matches the `"impr_id"` key from the example.
    """


class Author(CamelizeBaseModel):
    """
    TikTok user information.

    Example `author` object in the JSON:
    ```json
    "author": {
      "avatar_larger": "...",
      "avatar_medium": "...",
      "avatar_thumb": "...",
      "comment_setting": 0,
      "download_setting": 0,
      ...
    }
    ```
    """

    avatar_larger: str | None = None
    """URL to large version of user's avatar, e.g. `"avatar_larger": "https://.../1080x1080.jpeg"`"""

    avatar_medium: str | None = None
    """URL to medium version of user's avatar, e.g. `"avatar_medium": "https://.../720x720.jpeg"`"""

    avatar_thumb: str | None = None
    """URL to thumbnail version of user's avatar, e.g. `"avatar_thumb": "https://.../100x100.jpeg"`"""

    comment_setting: int | None = None
    """User's comment privacy setting, e.g. `0` indicates normal comment permissions."""

    download_setting: int | None = None
    """User's video download privacy setting, e.g. `0` if downloads are allowed."""

    duet_setting: int | None = None
    """User's duet privacy setting, e.g. `0` to allow duets."""

    ftc: bool | None = None
    """FTC-related flag, e.g. `false` in example data."""

    id: str | None = None
    """User's numeric ID, e.g. `"id": "7232670243117728773"` in the JSON."""

    is_ad_virtual: bool | None = Field(None, alias="isADVirtual")
    """Indicates if user is a virtual advertising account, 
    e.g. `"isADVirtual": false` in the JSON."""

    is_embed_banned: bool | None = None
    """Indicates if user is banned from video embedding, typically `false`."""

    nickname: str | None = None
    """User's display name, e.g. `"nickname": "Cristiano\ud83c\udf13"`."""

    open_favorite: bool | None = None
    """Indicates if user's favorites are public, e.g. `false` if private."""

    private_account: bool | None = None
    """Indicates if account is private, e.g. `false` if public."""

    relation: int | None = None
    """Relationship status with logged-in user, e.g. `0` means no direct relation."""

    sec_uid: str | None = None
    """User's security UID, e.g. `"sec_uid": "MS4wLjABAAAAXlMNlrh5..."`."""

    secret: bool | None = None
    """Indicates if account has additional privacy settings, e.g. `false`."""

    signature: str | None = None
    """User's profile bio, e.g. `"signature": "4/4 BREAKFAST CLUB..."`."""

    stitch_setting: int | None = None
    """User's stitch privacy setting, e.g. `0` if stitching is disabled."""

    unique_id: str | None = None
    """User's unique username, e.g. `"unique_id": "borsi___"` in the JSON."""

    verified: bool | None = None
    """Indicates if user is verified, e.g. `false`."""


class VideoStats(CamelizeBaseModel):
    """
    Video engagement statistics.

    Example 'stats' section from the JSON:
    ```json
    "stats": {
      "collect_count": 1307,
      "comment_count": 237,
      "digg_count": 14200,
      "play_count": 187200,
      "share_count": 4720
    }
    ```
    """

    collect_count: int | None = None
    """Number of times video has been saved, e.g. `1307`."""

    comment_count: int | None = None
    """Number of comments on the video, e.g. `237`."""

    digg_count: int | None = None
    """Number of likes on the video, e.g. `14200`."""

    play_count: int | None = None
    """Number of video plays, e.g. `187200`."""

    share_count: int | None = None
    """Number of times video has been shared, e.g. `4720`."""


class VideoStatsV2(CamelizeBaseModel):
    """
    Video engagement statistics (string-based).

    Some endpoints provide these fields as strings rather than integers.
    Example 'stats_v2' section from the JSON:
    ```json
    "stats_v2": {
      "collect_count": "1307",
      "comment_count": "237",
      "digg_count": "14200",
      "play_count": "187200",
      "repost_count": "0",
      "share_count": "4720"
    }
    ```
    """

    collect_count: str | None = None
    """Number of times video has been saved, stored as a string, e.g. `"1307"`."""

    comment_count: str | None = None
    """Number of comments on the video, stored as a string, e.g. `"237"`."""

    digg_count: str | None = None
    """Number of likes on the video, e.g. `"14200"`."""

    play_count: str | None = None
    """Number of video plays, e.g. `"187200"`."""

    repost_count: str | None = None
    """Number of times video has been reposted, e.g. `"0"`."""

    share_count: str | None = None
    """Number of times video has been shared, e.g. `"4720"`."""


class PlayAddress(PascalizeBaseModel):
    """
    Video playback address information.

    Example of a 'play_addr' structure within 'bitrate_info':
    ```json
    "play_addr": {
      "data_size": 1937754,
      "file_cs": "c:0-10011-dcaa",
      "file_hash": "7a3602a4635f6d0fa7954e5fe26b4a6e",
      "height": 1920,
      "uri": "v09044g40000cta735fog65sgeoufo10",
      "url_key": "...",
      "url_list": [...],
      "width": 1080
    }
    ```
    """

    data_size: int | None = None
    """Size of video file in bytes, e.g. `1937754`."""

    file_cs: str | None = None
    """File checksum, e.g. `"c:0-10011-dcaa"`."""

    file_hash: str | None = None
    """File hash identifier, e.g. `"7a3602a4635f6d0fa7954e5fe26b4a6e"`."""

    height: int | None = None
    """Video height in pixels, e.g. `1920`."""

    uri: str | None = None
    """Video URI identifier, e.g. `"v09044g40000cta735fog65sgeoufo10"`."""

    url_key: str | None = None
    """Key for video URL, e.g. `"v09044g40000cta735fog65sgeoufo10_bytevc1_1080p_1548964"`."""

    url_list: list[str] | None = None
    """List of video URLs for different CDNs, e.g. `[ "https://v16-webapp-prime.tiktok.com/..." ]`."""

    width: int | None = None
    """Video width in pixels, e.g. `1080`."""


class BitrateInfo(PascalizeBaseModel):
    """
    Video bitrate and quality information.

    Found in 'bitrate_info' arrays. Example snippet:
    ```json
    {
      "bitrate": 1548964,
      "codec_type": "h265_hvc1",
      "gear_name": "adapt_lowest_1080_1",
      "play_addr": {...},
      "quality_type": 2,
      "mvmaf": ...
    }
    ```
    """

    bitrate: int | None = None
    """Video bitrate in bits per second, e.g. `1548964`."""

    codec_type: str | None = None
    """Video codec (e.g., 'h264', 'h265')."""

    gear_name: str | None = None
    """Quality tier identifier, e.g. `'adapt_lowest_1080_1'`."""

    play_addr: PlayAddress | None = None
    """Playback address for this quality tier."""

    quality_type: int | None = None
    """Numeric indicator of video quality, e.g. `2`."""

    mvmaf: str | None = Field(None, alias="MVMAF")
    """Video quality assessment metric (raw JSON string), e.g. 
    `"\"{\\\"v2.0\\\": {\\\"srv1\\\": {\\\"v1080\\\": 89.182, ...}}}\""`."""


class OriginalLanguageInfo(CamelizeBaseModel):
    """
    Information about the original language of the video.

    Example from 'original_language_info':
    ```json
    "original_language_info": {
      "can_translate_real_time_no_check": true,
      "language": "ita-IT",
      "language_code": "it",
      "language_id": "26"
    }
    ```
    """

    can_translate_real_time_no_check: bool | None = None
    """Whether real-time translation is available without verification, e.g. `true`."""

    language: str | None = None
    """Language code with region (e.g., `'ita-IT'`)."""

    language_code: str | None = None
    """Two-letter language code (e.g., `'it'`)."""

    language_id: str | None = Field(None, alias="languageID")
    """Language ID, e.g. `"26"`."""


class SubtitleInfo(PascalizeBaseModel):
    """
    Information about a subtitle track.

    Example from 'subtitle_infos':
    ```json
    {
      "format": "webvtt",
      "language_code_name": "eng-US",
      "language_id": "2",
      "size": 6536,
      "source": "MT",
      "url": "https://v16-webapp.tiktok.com/e6b85bfe9e5fc6f5...",
      "url_expire": 1736881501,
      "version": "4"
    }
    ```
    """

    format: str | None = None
    """Format of the subtitle file (e.g., 'webvtt', 'creator_caption')."""

    language_code_name: str | None = None
    """Language code with region (e.g., 'eng-US', 'ita-IT')."""

    language_id: str | None = Field(None, alias="LanguageID")
    """Unique identifier for the language, e.g. `'2'` for English."""

    size: int | None = None
    """Size of the subtitle file in bytes, e.g. `6536`."""

    source: str | None = None
    """Source of the subtitles, e.g., `'MT'` (machine translation) or `'ASR'`."""

    url: str | None = None
    """URL to access the subtitle file."""

    url_expire: int | None = None
    """Timestamp when the URL expires, e.g., `1736881501`."""

    version: str | None = None
    """Version of the subtitle format, e.g. `'4'`."""


class CaptionInfo(CamelizeBaseModel):
    """
    Information about a specific caption/subtitle track.

    Appears in the 'caption_infos' array. Example snippet:
    ```json
    {
      "caption_format": "webvtt",
      "cla_subtitle_id": "7455675424673827606",
      "expire": "1736881501",
      "is_auto_gen": true,
      ...
    }
    ```
    """

    caption_format: str | None = None
    """Format of the caption file (e.g., 'webvtt')."""

    cla_subtitle_id: str | None = Field(None, alias="claSubtitleID")
    """Unique identifier for the subtitle, e.g. `'7455675631578336022'`."""

    expire: str | None = None
    """Expiration timestamp for the caption URL as a string, e.g. `'1736881501'`."""

    is_auto_gen: bool | None = None
    """Whether the caption was automatically generated, e.g. `true`."""

    is_original_caption: bool | None = None
    """Whether this is the original caption track, e.g. `true` or `false`."""

    language: str | None = None
    """Language code with region (e.g., `'eng-US'`)."""

    language_id: str | None = Field(None, alias="languageID")
    """Language ID, e.g. `'2'`."""

    sub_id: str | None = Field(None, alias="subID")
    """Subtitle ID, e.g. `'675411108'`."""

    language_code: str | None = None
    """Two-letter language code (e.g., 'en')."""

    subtitle_type: str | None = None
    """Type of subtitle (e.g., '4' for auto-generated, '1' for manual)."""

    translation_type: str | None = None
    """Type of translation, e.g. `'0'` if none."""

    url: str | None = None
    """URL to access the caption file, e.g. `'https://v16-webapp.tiktok.com/e6b85bfe...'`."""

    url_list: list[str] = Field(default_factory=list)
    """List of alternative URLs for the caption file, often containing multiple mirrors."""

    variant: str | None = None
    """Caption variant identifier, e.g. `'default'`."""


class ClaInfo(CamelizeBaseModel):
    """
    Complete caption information for a video.

    Example snippet from 'cla_info':
    ```json
    "cla_info": {
      "caption_infos": [...],
      "captions_type": 2,
      "enable_auto_caption": true,
      "original_language_info": { ... },
      "has_original_audio": true
    }
    ```
    """

    caption_infos: list[CaptionInfo] = Field(default_factory=list)
    """List of available caption tracks, each item describing a separate track."""

    captions_type: int | None = None
    """Type indicator for the captions, e.g. `'2'` in example data."""

    enable_auto_caption: bool | None = None
    """Whether automatic captioning is enabled, e.g. `true`."""

    original_language_info: OriginalLanguageInfo | None = None
    """Information about the video's original language, if present."""

    has_original_audio: bool | None = None
    """Indicates if video has original audio, e.g. `true`."""

    no_caption_reason: int | None = None
    """Reason for lack of captions, e.g. `'3'` if no captions exist."""


class VolumeInfo(PascalizeBaseModel):
    """
    Video volume information.

    Commonly found as `'volume_info'`. Example:
    ```json
    "volume_info": {
      "loudness": -13.4,
      "peak": 0.60954
    }
    ```
    """

    loudness: int | float | None = None
    """Audio loudness level, e.g. `-13.4`."""

    peak: int | float | None = None
    """Audio peak level, e.g. `0.60954`."""


class Video(CamelizeBaseModel):
    """
    Detailed video information.

    Example snippet from 'video':
    ```json
    "video": {
      "vq_score": "68.45",
      "bitrate": 1256012,
      "bitrate_info": [...],
      "cla_info": { ... },
      ...
    }
    ```
    """

    vq_score: str | None = Field(None, alias="VQScore")
    """Video quality score, e.g. `"68.45"`."""

    bitrate: int | None = None
    """Video bitrate in bits per second, e.g. `1256012`."""

    bitrate_info: list[BitrateInfo] = Field(default_factory=list, serialization_alias="bitrateInfo")
    """Available video quality versions, e.g. multiple BitrateInfo objects for different resolutions."""

    cla_info: ClaInfo | None = None
    """Video classification information (captions, original language, etc.)."""

    codec_type: str | None = None
    """Primary video codec, e.g. `'h264'` or `'h265_hvc1'`."""

    cover: str | None = None
    """URL of video cover image, e.g. `'https://p16-sign-va.tiktokcdn.com/obj/tos...'`."""

    definition: str | None = None
    """Video quality definition, e.g. `'540p'`."""

    download_addr: str | None = None
    """Video download URL if provided, e.g. `'https://v16-webapp-prime.tiktok.com/video/tos/useast2a...'`."""

    duration: int | None = None
    """Video duration in seconds, e.g. `10` or `154`."""

    dynamic_cover: str | None = None
    """URL of animated video cover, e.g. `'https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/...'`."""

    encode_user_tag: str | None = None
    """User tag for video encoding, often an empty string."""

    encoded_type: str | None = None
    """Video encoding type, e.g. `'normal'`."""

    format: str | None = None
    """Video format, e.g. `'mp4'`."""

    height: int | None = None
    """Video height in pixels, e.g. `1024`."""

    id: str | None = None
    """Video identifier, e.g. `'7445701530583436550'`."""

    origin_cover: str | None = None
    """URL of original cover image, sometimes distinct from 'cover'."""

    play_addr: str | None = None
    """Primary video playback URL, e.g. `'https://v16-webapp-prime.tiktok.com/video/tos...'`."""

    ratio: str | None = None
    """Video aspect ratio (e.g., `'540p'`, `'720p'`)."""

    subtitle_infos: list[SubtitleInfo] = Field(default_factory=list)
    """List of subtitle info objects if any. See `SubtitleInfo`."""

    video_quality: str | None = None
    """Video quality level, e.g. `'normal'`."""

    volume_info: VolumeInfo | None = None
    """Video volume information (loudness, peak)."""

    width: int | None = None
    """Video width in pixels, e.g. `576`."""

    zoom_cover: dict[str, str] | None = None
    """Zoomed-in video cover image with a size<->URL mapping, e.g. `{"240": "https://...", "480": "https://..."}`."""


class Music(CamelizeBaseModel):
    """
    Audio track information.

    Example from 'music':
    ```json
    "music": {
      "album": null,
      "author_name": "chubby_s_life",
      "cover_large": "...",
      "cover_medium": "...",
      "cover_thumb": "...",
      "duration": 57,
      "id": "7368542661508549409",
      ...
    }
    ```
    """

    album: str | None = None
    """Album name, e.g. `'myAlbum'` or `null` if not provided."""

    author_name: str | None = None
    """Creator of the audio track, e.g. `'chubby_s_life'`."""

    cover_large: str | None = None
    """URL to large audio cover image."""

    cover_medium: str | None = None
    """URL to medium audio cover image."""

    cover_thumb: str | None = None
    """URL to thumbnail audio cover image."""

    duration: int | None = None
    """Audio duration in seconds, e.g. `57`."""

    id: str | None = None
    """Audio track identifier, e.g. `'7368542661508549409'`."""

    is_copyrighted: bool | None = None
    """Indicates if audio track is copyrighted, e.g. `false`."""

    original: bool | None = None
    """Indicates if audio track is original, e.g. `false`."""

    play_url: str | None = None
    """URL for playing the audio, if available."""

    title: str | None = None
    """Audio track title, e.g. `'son original - Cat'slife'`."""


class AnchorsExtra(CamelizeBaseModel):
    """
    Anchor extra information.

    Not heavily detailed in the snippet, but typically includes extra
    metadata for an anchor object, e.g. `'subtype'`.
    """

    subtype: str | None = None
    """Anchor subtype, e.g. `'some_subtype'`."""


class Icon(CamelizeBaseModel):
    """
    Icon information.

    Typically includes a list of URLs for the anchor or challenge icon.
    """

    url_list: list[str] | None = None
    """List of icon URLs, e.g. `[ "https://p16-", "https://..."]`."""


class Thumbnail(CamelizeBaseModel):
    """
    Thumbnail information for an anchor.

    Usually has a list of URLs, plus dimension fields.
    """

    url_list: list[str] | None = None
    """List of thumbnail URLs, e.g. `[ "https://...", "https://..."]`."""

    height: int | None = None
    """Thumbnail height in pixels."""

    width: int | None = None
    """Thumbnail width in pixels."""


class Anchors(CamelizeBaseModel):
    """
    Anchor information.

    Example structure might contain fields like 'id', 'description', 'keyword', etc.
    """

    description: str | None = None
    """Anchor description, e.g. `'Anchor text'`."""

    extra_info: AnchorsExtra | None = None
    """Additional anchor information such as subtype."""

    icon: Icon | None = None
    """Anchor icon information. Contains `url_list`."""

    id: str | None = None
    """Anchor identifier, e.g. `'anchor_id_123'`."""

    keyword: str | None = None
    """Anchor keyword, e.g. `'keyword_value'`."""

    log_extra: str | None = None
    """Anchor logging information, e.g. `'extra logging info'`."""

    anchor_schema: str | None = Field(None, alias="schema")
    """Anchor schema, e.g. `'schema_value'`."""

    thumbnail: Thumbnail | None = None
    """Anchor thumbnail information."""

    type: int | None = None
    """Anchor type, e.g. `0` or `1`."""


class TextExtra(CamelizeBaseModel):
    """
    Additional text information (hashtags, mentions, etc.).

    Example from 'text_extra':
    ```json
    {
      "aweme_id": "",
      "end": 30,
      "hashtag_name": "cat",
      "is_commerce": false,
      "sec_uid": null,
      "start": 26,
      "type": 1,
      ...
    }
    ```
    """

    aweme_id: str | None = None
    """Related video ID, e.g. `""` if not referencing another video."""

    end: int | None = None
    """End position of the text in description, e.g. `30`."""

    hashtag_name: str | None = None
    """Name of hashtag if present, e.g. `"cat"`."""

    is_commerce: bool | None = None
    """Indicates if text is commerce-related, e.g. `false`."""

    sec_uid: str | None = None
    """Security UID of related user, e.g. `null` if no user reference."""

    start: int | None = None
    """Start position of the text in description, e.g. `26`."""

    type: int | None = None
    """Type of text extra, e.g. `1` for hashtag, `0` for mention."""

    user_id: str | None = None
    """Related user ID if mention is a user, e.g. `null` or `'6834929968847143941'`."""

    user_unique_id: str | None = None
    """Related user unique ID, e.g. `'violasilvii'`."""

    sub_type: int | None = None
    """Subtype for the mention or hashtag, e.g. `0`."""


class Content(CamelizeBaseModel):
    """
    Video content information.

    Each object typically has a short 'desc' plus an optional 'text_extra' array.
    """

    desc: str | None = None
    """Content description, e.g. `'Fiat Panda 1.3 MULTIJET'` or `'SOLO IO HO AVUTO UN DEJAVÙ?'`."""

    text_extra: list[TextExtra] = Field(default_factory=list)
    """List of text extras, e.g. hashtags or mentions."""


class Challenge(CamelizeBaseModel):
    """
    Hashtag challenge information.

    Example from 'challenges':
    ```json
    {
      "cover_larger": "",
      "cover_medium": "",
      ...
      "desc": "",
      "id": "36351816",
      "title": "republication"
    }
    ```
    """

    cover_larger: str | None = None
    """URL to large challenge cover image, often empty string `""` if not present."""

    cover_medium: str | None = None
    """URL to medium challenge cover image."""

    cover_thumb: str | None = None
    """URL to thumbnail challenge cover image."""

    desc: str | None = None
    """Challenge description, possibly `""` if absent."""

    id: str | None = None
    """Challenge identifier, e.g. `"36351816"`."""

    profile_larger: str | None = None
    """URL to large challenge profile image, e.g. `""` or a direct link."""

    profile_medium: str | None = None
    """URL to medium challenge profile image."""

    profile_thumb: str | None = None
    """URL to thumbnail challenge profile image."""

    title: str | None = None
    """Challenge title/name, e.g. `"republication"`."""


class ItemControl(BaseModel):
    """
    Item control information.

    Typically found as `"item_control": { ... }` in the JSON.
    """

    can_repost: bool | None = None
    """Indicates if video can be reposted, e.g. `true`."""

    can_comment: bool | None = None
    """Indicates if video can be commented on, e.g. `null` or `true`."""

    can_creator_redirect: bool | None = None
    """Indicates if creator redirect is enabled."""

    can_music_redirect: bool | None = None
    """Indicates if music redirect is enabled."""

    can_share: bool | None = None
    """Indicates if video can be shared."""


class PointOfInterest(CamelizeBaseModel):
    """
    Model representing a Point of Interest (POI) from TikTok.

    Not demonstrated thoroughly in the sample data, but can appear
    if the video is tagged with a location or place info.
    """

    address: str | None = None
    """Physical address of the POI, e.g. `'1234 Sample St.'`."""

    category: str | None = None
    """Category classification of the POI, e.g. `'Restaurant'`."""

    city: str | None = None
    """City name, e.g. `'New York'`."""

    city_code: str | None = None
    """Numeric code identifying the city, e.g. `'1234'`."""

    country: str | None = None
    """Country name, e.g. `'US'`."""

    country_code: str | None = None
    """Numeric code identifying the country, e.g. `'840'` for the US."""

    father_poi_id: str | None = None
    """ID of the parent POI if this is a sub-location."""

    father_poi_name: str | None = None
    """Name of the parent POI if this is a sub-location."""

    id: str | None = None
    """Unique identifier for the POI, e.g. `'poi123'`."""

    name: str | None = None
    """Name of the POI, e.g. `'Central Park'`."""

    province: str | None = None
    """Province/state name, e.g. `'New York'`."""

    tt_type_code: str | None = None
    """TikTok internal type code, e.g. `'code_xyz'`."""

    tt_type_name_medium: str | None = None
    """Medium-level classification name, e.g. `'Public Park'`."""

    tt_type_name_super: str | None = None
    """Top-level classification name, e.g. `'Outdoor'`."""

    tt_type_name_tiny: str | None = None
    """Detailed classification name, e.g. `'Urban Park'`."""

    type: int
    """Numeric type identifier, e.g. `1`."""

    type_code: str = Field(serialization_alias="typeCode")
    """String type code, e.g. `'xyz'`."""


class TikTokVideo(CamelizeBaseModel):
    """
    Complete TikTok video information.

    One example 'item' in the JSON might look like:
    ```json
    {
      "id": "7445701530583436550",
      "desc": "...",
      "challenges": [...],
      "author": {...},
      "music": {...},
      "video": {...},
      "stats": {...},
      "stats_v2": {...},
      ...
    }
    ```
    """

    aigc_description: str | None = Field(None, alias="AIGCDescription")
    """AI-generated video description, if present, e.g. `""` if not provided."""

    ba_info: str | None = Field(None, alias="BAInfo")
    """Unknown video information, typically `null`."""

    category_type: int | None = Field(None, alias="CategoryType")
    """Video category type, e.g. `110` or `111` in your sample data."""

    ad_authorization: bool | None = None
    """Indicates if video is authorized for advertising, e.g. `null` or `false`."""

    ad_label_version: int | None = None
    """Advertising label version, e.g. `null` if not used."""

    anchors: list[Anchors] = Field(default_factory=list)
    """List of anchor objects, if any. Often empty."""

    author: Author
    """Video creator information. See `Author` model."""

    backend_source_event_tracking: str | None = None
    """String marker for event tracking, e.g. `"fyp_35"`."""

    challenges: list[Challenge] | None = None
    """Associated hashtag challenges, see `Challenge` model."""

    collected: bool | None = None
    """Indicates if video has been saved (favorited) by the current user."""

    contents: list[Content] = Field(default_factory=list)
    """Video content array. Each `Content` has a desc plus optional text extras."""

    create_time: int | None = None
    """Video creation timestamp, e.g. `1735909582`."""

    desc: str | None = None
    """Video description/caption, e.g. `"Fiat Panda 1.3 MULTIJET..."`."""

    digged: bool | None = None
    """Whether current user has liked (dug) the video, e.g. `false`."""

    diversification_id: int | None = None
    """Diversification ID, e.g. `10042` or `null`."""

    duet_display: int | None = None
    """Duet display setting, e.g. `0` for hidden, `1` for visible."""

    duet_enabled: bool | None = None
    """Indicates if duets are enabled, e.g. `true` or `null`."""

    for_friend: bool | None = None
    """Indicates if video is for friends only, e.g. `false`."""

    id: str
    """Video identifier, e.g. `"7445701530583436550"`."""

    item_comment_status: int | None = None
    """Comment status, e.g. `0` if normal or `1` if restricted."""

    item_control: ItemControl | None = Field(None, alias="item_control")
    """Settings for sharing, commenting, etc. See `ItemControl` model."""

    music: Music | None = None
    """Video audio track information. See `Music` model."""

    offical_item: bool | None = None
    """Indicates if video is official content, e.g. `false`."""

    original_item: bool | None = None
    """Indicates if video is original content, e.g. `false`."""

    poi: PointOfInterest | None = None
    """Point of interest information if the video is location-tagged."""

    private_item: bool | None = None
    """Indicates if video is private, e.g. `false`."""

    secret: bool | None = None
    """Secret status, e.g. `false` if normal."""

    share_enabled: bool | None = None
    """Indicates if video sharing is enabled, e.g. `true`."""

    stats: VideoStats | None = None
    """Video engagement statistics. See `VideoStats` model."""

    stats_v2: VideoStatsV2 | None = Field(None, alias="statsV2")
    """Additional video engagement statistics, see `VideoStatsV2` model."""

    stitch_display: int | None = None
    """Stitch display setting, e.g. `0` for hidden."""

    stitch_enabled: bool | None = None
    """Indicates if stitching is enabled, e.g. `true` or `false`."""

    text_extra: list[TextExtra] = Field(default_factory=list)
    """Additional text information in the video description, e.g. hashtags, mentions."""

    text_language: str | None = None
    """Language of video description, e.g. `"es"` or `"it"`."""

    text_translatable: bool | None = None
    """Indicates if video description is translatable, e.g. `true`."""

    video: Video
    """Technical video information, see `Video` model."""

    def to_llm(self) -> dict[str, Any]:
        """
        Returns a simplified dictionary containing the video information.
        """
        hashtags = []
        # Extract hashtags from the text_extra field at the TikTokVideo level.
        for item in self.text_extra:
            if item.hashtag_name:
                hashtags.append(item.hashtag_name)
        # Also check each content block's text_extra field.
        for content in self.contents:
            for extra in content.text_extra or []:
                if extra.hashtag_name:
                    hashtags.append(extra.hashtag_name)
        hashtags = list(set(hashtags))  # Remove duplicates

        return {
            "id": self.id,
            "description": self.desc,
            "aigc_description": self.aigc_description,
            "author_info": {
                "id": self.author.id,
                "nickname": self.author.nickname,
                "unique_id": self.author.unique_id,
            },
            "music_title": self.music.title if self.music else None,
            "duration": self.video.duration if self.video else None,
            "stats": {
                "plays": self.stats.play_count,
                "likes": self.stats.digg_count,
                "comments": self.stats.comment_count,
                "shares": self.stats.share_count,
            }
            if self.stats
            else None,
            "digged": self.digged,
            "collected": self.collected,
            "share_enabled": self.share_enabled,
            "backend_event": self.backend_source_event_tracking,
            "challenges": [challenge.title for challenge in self.challenges]
            if self.challenges
            else [],
            "poi": self.poi.name if self.poi else None,
            "text_language": self.text_language,
            "stitch_enabled": self.stitch_enabled,
            "hashtags": hashtags,
            "create_time": self.create_time,
        }


class User(CamelizeBaseModel):
    uid: str | None = None
    """User ID, e.g. '7372700493900645422'"""

    nickname: str | None = None
    """Display name, e.g. 'President Donald J Trump'"""

    signature: str | None = None
    """Bio/signature text, e.g. '45th President of the United States'"""

    avatar_thumb: dict[str, Any] | None = None
    """Thumbnail avatar image information including URI and URLs"""

    follow_status: int | None = None
    """Follow status code, e.g. 0"""

    follower_count: int | None = None
    """Number of followers, e.g. 15100000"""

    custom_verify: str | None = None
    """Custom verification text"""

    unique_id: str | None = None
    """Unique username, e.g. 'realdonaldtrump'"""

    room_id: int | None = None
    """Room ID number"""

    enterprise_verify_reason: str | None = None
    """Enterprise verification text, e.g. 'institution account'"""

    followers_detail: Any | None = None
    """Detailed follower information"""

    platform_sync_info: Any | None = None
    """Platform sync information"""

    geofencing: Any | None = None
    """Geofencing settings"""

    cover_url: Any | None = None
    """Cover image URL"""

    item_list: Any | None = None
    """List of items"""

    type_label: Any | None = None
    """Type label information"""

    ad_cover_url: Any | None = None
    """Advertisement cover URL"""

    relative_users: Any | None = None
    """Related user information"""

    cha_list: Any | None = None
    """Challenge list information"""

    sec_uid: str | None = None
    """Security user ID"""

    need_points: Any | None = None
    """Points requirement information"""

    homepage_bottom_toast: Any | None = None
    """Homepage bottom toast information"""

    can_set_geofencing: Any | None = None
    """Geofencing permission flag"""

    white_cover_url: Any | None = None
    """White cover image URL"""

    user_tags: Any | None = None
    """User tag information"""

    bold_fields: Any | None = None
    """Bold field settings"""

    search_highlight: Any | None = None
    """Search highlight information"""

    mutual_relation_avatars: Any | None = None
    """Mutual relation avatar information"""

    room_id_str: str | None = None
    """Room ID as string"""

    events: Any | None = None
    """Event information"""

    advance_feature_item_order: Any | None = None
    """Advanced feature item order"""

    advanced_feature_info: Any | None = None
    """Advanced feature information"""

    user_profile_guide: Any | None = None
    """User profile guide information"""

    shield_edit_field_info: Any | None = None
    """Shield edit field information"""

    can_message_follow_status_list: Any | None = None
    """Message and follow status list"""

    account_labels: Any | None = None
    """Account label information"""
