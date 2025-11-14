"""
Data models for Octo Browser API.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Proxy:
    """Proxy configuration."""

    type: str = "http"  # http, https, socks5
    host: str = ""
    port: int = 0
    username: Optional[str] = None
    password: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Proxy":
        """Create from dictionary."""
        return cls(
            type=data.get("type", "http"),
            host=data.get("host", ""),
            port=data.get("port", 0),
            username=data.get("username"),
            password=data.get("password"),
        )


@dataclass
class Tag:
    """Profile tag."""

    uuid: str = ""
    name: str = ""
    color: str = "#000000"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"uuid": self.uuid, "name": self.name, "color": self.color}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tag":
        """Create from dictionary."""
        return cls(
            uuid=data.get("uuid", ""),
            name=data.get("name", ""),
            color=data.get("color", "#000000"),
        )


@dataclass
class Fingerprint:
    """Browser fingerprint configuration."""

    os: str = "win"  # win, mac, lin
    screen_resolution: str = "1920x1080"
    webgl_vendor: str = ""
    webgl_renderer: str = ""
    user_agent: str = ""
    language: str = "en-US"
    timezone: str = "America/New_York"
    geolocation: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "os": self.os,
            "screen": self.screen_resolution,
            "webgl_vendor": self.webgl_vendor,
            "webgl_renderer": self.webgl_renderer,
            "user_agent": self.user_agent,
            "language": self.language,
            "timezone": self.timezone,
            "geolocation": self.geolocation,
        }


@dataclass
class Profile:
    """Octo Browser profile."""

    uuid: str = ""
    title: str = "New Profile"
    description: str = ""
    tags: List[Tag] = field(default_factory=list)
    proxy: Optional[Proxy] = None
    fingerprint: Fingerprint = field(default_factory=Fingerprint)

    # Status
    status: str = "INACTIVE"  # ACTIVE, INACTIVE

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Settings
    start_url: str = "about:blank"
    cookies: List[Dict[str, Any]] = field(default_factory=list)
    bookmarks: List[str] = field(default_factory=list)
    extensions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API."""
        return {
            "uuid": self.uuid,
            "title": self.title,
            "description": self.description,
            "tags": [tag.to_dict() for tag in self.tags],
            "proxy": self.proxy.to_dict() if self.proxy else None,
            "fingerprint": self.fingerprint.to_dict(),
            "start_url": self.start_url,
            "cookies": self.cookies,
            "bookmarks": self.bookmarks,
            "extensions": self.extensions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Profile":
        """Create from API response."""
        tags = [Tag.from_dict(t) for t in data.get("tags", [])]
        proxy = Proxy.from_dict(data["proxy"]) if data.get("proxy") else None

        return cls(
            uuid=data.get("uuid", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            tags=tags,
            proxy=proxy,
            status=data.get("status", "INACTIVE"),
            start_url=data.get("start_url", "about:blank"),
            cookies=data.get("cookies", []),
            bookmarks=data.get("bookmarks", []),
            extensions=data.get("extensions", []),
        )

    def add_tag(self, tag: Tag):
        """Add tag to profile."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag_uuid: str):
        """Remove tag from profile."""
        self.tags = [t for t in self.tags if t.uuid != tag_uuid]

    def set_proxy(self, proxy: Proxy):
        """Set proxy for profile."""
        self.proxy = proxy

    def __repr__(self) -> str:
        return f"Profile(uuid={self.uuid[:8]}, title={self.title}, status={self.status})"
