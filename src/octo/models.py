"""
Data models for Octo Browser integration.

Defines models for profiles, proxies, tags, and fingerprints.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProfileStatus(Enum):
    """Profile status."""

    ACTIVE = 0
    INACTIVE = 1
    DELETED = 2


class ProxyType(Enum):
    """Proxy connection type."""

    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"
    SSH = "ssh"


class BrowserType(Enum):
    """Browser type."""

    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"


@dataclass
class Proxy:
    """Octo Browser proxy configuration."""

    type: ProxyType
    host: str
    port: int
    login: Optional[str] = None
    password: Optional[str] = None
    change_ip_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        result = {
            "type": self.type.value,
            "host": self.host,
            "port": self.port,
        }

        if self.login:
            result["login"] = self.login
        if self.password:
            result["password"] = self.password
        if self.change_ip_url:
            result["change_ip_url"] = self.change_ip_url

        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Proxy":
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            Proxy instance
        """
        return Proxy(
            type=ProxyType(data.get("type", "http")),
            host=data["host"],
            port=data["port"],
            login=data.get("login"),
            password=data.get("password"),
            change_ip_url=data.get("change_ip_url"),
        )

    def __str__(self) -> str:
        """String representation.

        Returns:
            Proxy string
        """
        if self.login and self.password:
            return f"{self.type.value}://{self.login}:{self.password}@{self.host}:{self.port}"
        return f"{self.type.value}://{self.host}:{self.port}"


@dataclass
class Tag:
    """Octo Browser tag."""

    uuid: str
    name: str
    color: str = "#808080"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "uuid": self.uuid,
            "name": self.name,
            "color": self.color,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Tag":
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            Tag instance
        """
        return Tag(
            uuid=data["uuid"],
            name=data["name"],
            color=data.get("color", "#808080"),
        )


@dataclass
class Fingerprint:
    """Browser fingerprint configuration."""

    # Screen
    screen_resolution: str = "1920x1080"
    screen_color_depth: int = 24

    # WebGL
    webgl_vendor: Optional[str] = None
    webgl_renderer: Optional[str] = None

    # Canvas
    canvas_noise: bool = True

    # Audio
    audio_noise: bool = True

    # Fonts
    fonts: List[str] = field(default_factory=list)

    # Navigator
    user_agent: Optional[str] = None
    platform: Optional[str] = None
    language: str = "en-US"
    languages: List[str] = field(default_factory=lambda: ["en-US", "en"])

    # Hardware
    hardware_concurrency: Optional[int] = None
    device_memory: Optional[int] = None

    # Media devices
    media_devices: Optional[Dict[str, Any]] = None

    # Geolocation
    geolocation: Optional[Dict[str, float]] = None  # {"latitude": 0.0, "longitude": 0.0}

    # Timezone
    timezone: str = "America/New_York"

    # WebRTC
    webrtc_public_ip: Optional[str] = None
    webrtc_local_ip: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        result = {
            "screen": {
                "resolution": self.screen_resolution,
                "color_depth": self.screen_color_depth,
            },
            "canvas_noise": self.canvas_noise,
            "audio_noise": self.audio_noise,
            "navigator": {
                "language": self.language,
                "languages": self.languages,
            },
            "timezone": self.timezone,
        }

        if self.webgl_vendor:
            result["webgl"] = {
                "vendor": self.webgl_vendor,
                "renderer": self.webgl_renderer,
            }

        if self.fonts:
            result["fonts"] = self.fonts

        if self.user_agent:
            result["navigator"]["user_agent"] = self.user_agent

        if self.platform:
            result["navigator"]["platform"] = self.platform

        if self.hardware_concurrency:
            result["navigator"]["hardware_concurrency"] = self.hardware_concurrency

        if self.device_memory:
            result["navigator"]["device_memory"] = self.device_memory

        if self.media_devices:
            result["media_devices"] = self.media_devices

        if self.geolocation:
            result["geolocation"] = self.geolocation

        if self.webrtc_public_ip or self.webrtc_local_ip:
            result["webrtc"] = {}
            if self.webrtc_public_ip:
                result["webrtc"]["public_ip"] = self.webrtc_public_ip
            if self.webrtc_local_ip:
                result["webrtc"]["local_ip"] = self.webrtc_local_ip

        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Fingerprint":
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            Fingerprint instance
        """
        fp = Fingerprint()

        if "screen" in data:
            fp.screen_resolution = data["screen"].get("resolution", "1920x1080")
            fp.screen_color_depth = data["screen"].get("color_depth", 24)

        if "webgl" in data:
            fp.webgl_vendor = data["webgl"].get("vendor")
            fp.webgl_renderer = data["webgl"].get("renderer")

        fp.canvas_noise = data.get("canvas_noise", True)
        fp.audio_noise = data.get("audio_noise", True)

        if "fonts" in data:
            fp.fonts = data["fonts"]

        if "navigator" in data:
            nav = data["navigator"]
            fp.user_agent = nav.get("user_agent")
            fp.platform = nav.get("platform")
            fp.language = nav.get("language", "en-US")
            fp.languages = nav.get("languages", ["en-US", "en"])
            fp.hardware_concurrency = nav.get("hardware_concurrency")
            fp.device_memory = nav.get("device_memory")

        if "media_devices" in data:
            fp.media_devices = data["media_devices"]

        if "geolocation" in data:
            fp.geolocation = data["geolocation"]

        fp.timezone = data.get("timezone", "America/New_York")

        if "webrtc" in data:
            fp.webrtc_public_ip = data["webrtc"].get("public_ip")
            fp.webrtc_local_ip = data["webrtc"].get("local_ip")

        return fp


@dataclass
class Profile:
    """Octo Browser profile."""

    uuid: str
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)  # List of tag UUIDs
    proxy: Optional[Proxy] = None
    status: ProfileStatus = ProfileStatus.ACTIVE
    fingerprint: Optional[Fingerprint] = None

    # Browser settings
    browser_type: BrowserType = BrowserType.CHROME
    start_url: str = "about:blank"

    # Extensions
    extensions: List[str] = field(default_factory=list)

    # Bookmarks
    bookmarks: List[Dict[str, str]] = field(default_factory=list)

    # Notes
    notes: str = ""

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_opened_at: Optional[datetime] = None

    # Custom data
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API.

        Returns:
            Dictionary representation
        """
        result = {
            "uuid": self.uuid,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "status": self.status.value,
            "browser_type": self.browser_type.value,
            "start_url": self.start_url,
            "extensions": self.extensions,
            "bookmarks": self.bookmarks,
            "notes": self.notes,
        }

        if self.proxy:
            result["proxy"] = self.proxy.to_dict()

        if self.fingerprint:
            result["fingerprint"] = self.fingerprint.to_dict()

        if self.custom_data:
            result["custom_data"] = self.custom_data

        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Profile":
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            Profile instance
        """
        profile = Profile(
            uuid=data["uuid"],
            title=data["title"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
            status=ProfileStatus(data.get("status", 0)),
            browser_type=BrowserType(data.get("browser_type", "chrome")),
            start_url=data.get("start_url", "about:blank"),
            extensions=data.get("extensions", []),
            bookmarks=data.get("bookmarks", []),
            notes=data.get("notes", ""),
            custom_data=data.get("custom_data", {}),
        )

        if "proxy" in data and data["proxy"]:
            profile.proxy = Proxy.from_dict(data["proxy"])

        if "fingerprint" in data and data["fingerprint"]:
            profile.fingerprint = Fingerprint.from_dict(data["fingerprint"])

        # Parse timestamps
        if "created_at" in data and data["created_at"]:
            try:
                profile.created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                pass

        if "updated_at" in data and data["updated_at"]:
            try:
                profile.updated_at = datetime.fromisoformat(data["updated_at"])
            except (ValueError, TypeError):
                pass

        if "last_opened_at" in data and data["last_opened_at"]:
            try:
                profile.last_opened_at = datetime.fromisoformat(data["last_opened_at"])
            except (ValueError, TypeError):
                pass

        return profile

    def add_tag(self, tag_uuid: str) -> None:
        """Add tag to profile.

        Args:
            tag_uuid: Tag UUID
        """
        if tag_uuid not in self.tags:
            self.tags.append(tag_uuid)

    def remove_tag(self, tag_uuid: str) -> None:
        """Remove tag from profile.

        Args:
            tag_uuid: Tag UUID
        """
        if tag_uuid in self.tags:
            self.tags.remove(tag_uuid)

    def has_tag(self, tag_uuid: str) -> bool:
        """Check if profile has tag.

        Args:
            tag_uuid: Tag UUID

        Returns:
            True if has tag
        """
        return tag_uuid in self.tags


@dataclass
class ProfileCreateRequest:
    """Request to create new profile."""

    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    proxy: Optional[Proxy] = None
    fingerprint: Optional[Fingerprint] = None
    browser_type: BrowserType = BrowserType.CHROME
    start_url: str = "about:blank"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        result = {
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "browser_type": self.browser_type.value,
            "start_url": self.start_url,
        }

        if self.proxy:
            result["proxy"] = self.proxy.to_dict()

        if self.fingerprint:
            result["fingerprint"] = self.fingerprint.to_dict()

        return result


@dataclass
class ProfileUpdateRequest:
    """Request to update profile."""

    uuid: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    proxy: Optional[Proxy] = None
    status: Optional[ProfileStatus] = None
    start_url: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation with only set fields
        """
        result = {"uuid": self.uuid}

        if self.title is not None:
            result["title"] = self.title

        if self.description is not None:
            result["description"] = self.description

        if self.tags is not None:
            result["tags"] = self.tags

        if self.proxy is not None:
            result["proxy"] = self.proxy.to_dict()

        if self.status is not None:
            result["status"] = self.status.value

        if self.start_url is not None:
            result["start_url"] = self.start_url

        if self.notes is not None:
            result["notes"] = self.notes

        return result


@dataclass
class BulkOperationResult:
    """Result of bulk operation."""

    total: int
    successful: int
    failed: int
    errors: List[Dict[str, str]] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Get success rate.

        Returns:
            Success rate (0.0 to 1.0)
        """
        if self.total == 0:
            return 0.0
        return self.successful / self.total

    def add_success(self) -> None:
        """Add successful operation."""
        self.successful += 1
        self.total += 1

    def add_failure(self, profile_id: str, error: str) -> None:
        """Add failed operation.

        Args:
            profile_id: Profile UUID
            error: Error message
        """
        self.failed += 1
        self.total += 1
        self.errors.append({"profile_id": profile_id, "error": error})

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "errors": self.errors,
        }
