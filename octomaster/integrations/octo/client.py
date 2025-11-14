"""
Octo Browser API Client.

Provides full integration with Octo Browser API for managing profiles,
proxies, tags, and browser automation.
"""

import httpx
from typing import List, Dict, Any, Optional
from loguru import logger

from octomaster.integrations.octo.models import Profile, Proxy, Tag


class OctoAPIException(Exception):
    """Exception for Octo API errors."""

    pass


class OctoClient:
    """
    Client for Octo Browser API.

    Provides methods for:
    - Profile management (create, read, update, delete)
    - Proxy management
    - Tag management
    - Browser automation (start, stop profiles)
    - Bulk operations
    """

    def __init__(self, api_key: str, api_url: str = "https://api.octobrowser.net"):
        """
        Initialize Octo Browser client.

        Args:
            api_key: Your Octo Browser API key
            api_url: API base URL (default: https://api.octobrowser.net)
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.client = httpx.AsyncClient(
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        logger.info(f"Octo Browser client initialized: {api_url}")

    async def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Make API request."""
        url = f"{self.api_url}{endpoint}"

        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            raise OctoAPIException(
                f"API error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise OctoAPIException(f"Request failed: {e}")

    # ========== Profile Management ==========

    async def list_profiles(
        self,
        page: int = 1,
        limit: int = 50,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
    ) -> List[Profile]:
        """
        Get list of profiles.

        Args:
            page: Page number (1-indexed)
            limit: Items per page (max 100)
            tags: Filter by tag UUIDs
            search: Search query

        Returns:
            List of Profile objects
        """
        params = {"page": page, "limit": limit}

        if tags:
            params["tags"] = ",".join(tags)
        if search:
            params["search"] = search

        data = await self._request("GET", "/profiles", params=params)

        profiles = [Profile.from_dict(p) for p in data.get("data", [])]
        logger.info(f"Retrieved {len(profiles)} profiles")

        return profiles

    async def get_profile(self, profile_uuid: str) -> Profile:
        """
        Get profile by UUID.

        Args:
            profile_uuid: Profile UUID

        Returns:
            Profile object
        """
        data = await self._request("GET", f"/profiles/{profile_uuid}")
        profile = Profile.from_dict(data)

        logger.info(f"Retrieved profile: {profile.title}")
        return profile

    async def create_profile(self, profile: Profile) -> Profile:
        """
        Create new profile.

        Args:
            profile: Profile object

        Returns:
            Created Profile with UUID
        """
        data = await self._request("POST", "/profiles", json=profile.to_dict())
        created_profile = Profile.from_dict(data)

        logger.info(f"Created profile: {created_profile.title} ({created_profile.uuid})")
        return created_profile

    async def update_profile(self, profile: Profile) -> Profile:
        """
        Update existing profile.

        Args:
            profile: Profile object with UUID

        Returns:
            Updated Profile
        """
        if not profile.uuid:
            raise ValueError("Profile UUID is required for update")

        data = await self._request(
            "PUT", f"/profiles/{profile.uuid}", json=profile.to_dict()
        )
        updated_profile = Profile.from_dict(data)

        logger.info(f"Updated profile: {updated_profile.title}")
        return updated_profile

    async def delete_profile(self, profile_uuid: str) -> bool:
        """
        Delete profile.

        Args:
            profile_uuid: Profile UUID

        Returns:
            True if successful
        """
        await self._request("DELETE", f"/profiles/{profile_uuid}")
        logger.info(f"Deleted profile: {profile_uuid}")
        return True

    async def duplicate_profile(self, profile_uuid: str) -> Profile:
        """
        Duplicate existing profile.

        Args:
            profile_uuid: Profile UUID to duplicate

        Returns:
            New Profile (duplicate)
        """
        data = await self._request("POST", f"/profiles/{profile_uuid}/duplicate")
        duplicated = Profile.from_dict(data)

        logger.info(f"Duplicated profile: {duplicated.title}")
        return duplicated

    # ========== Profile Actions ==========

    async def start_profile(
        self, profile_uuid: str, debug_port: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Start browser profile.

        Args:
            profile_uuid: Profile UUID
            debug_port: Optional debug port for CDP connection

        Returns:
            Connection info with debug port and ws endpoint
        """
        params = {}
        if debug_port:
            params["debug_port"] = debug_port

        data = await self._request(
            "POST", f"/profiles/{profile_uuid}/start", params=params
        )

        logger.info(f"Started profile: {profile_uuid}")
        return data

    async def stop_profile(self, profile_uuid: str) -> bool:
        """
        Stop browser profile.

        Args:
            profile_uuid: Profile UUID

        Returns:
            True if successful
        """
        await self._request("POST", f"/profiles/{profile_uuid}/stop")
        logger.info(f"Stopped profile: {profile_uuid}")
        return True

    async def get_profile_status(self, profile_uuid: str) -> str:
        """
        Get profile running status.

        Args:
            profile_uuid: Profile UUID

        Returns:
            Status: "ACTIVE" or "INACTIVE"
        """
        data = await self._request("GET", f"/profiles/{profile_uuid}/status")
        return data.get("status", "INACTIVE")

    # ========== Tag Management ==========

    async def list_tags(self) -> List[Tag]:
        """
        Get list of all tags.

        Returns:
            List of Tag objects
        """
        data = await self._request("GET", "/tags")
        tags = [Tag.from_dict(t) for t in data.get("data", [])]

        logger.info(f"Retrieved {len(tags)} tags")
        return tags

    async def create_tag(self, name: str, color: str = "#000000") -> Tag:
        """
        Create new tag.

        Args:
            name: Tag name
            color: Tag color (hex)

        Returns:
            Created Tag
        """
        data = await self._request(
            "POST", "/tags", json={"name": name, "color": color}
        )
        tag = Tag.from_dict(data)

        logger.info(f"Created tag: {tag.name}")
        return tag

    async def delete_tag(self, tag_uuid: str) -> bool:
        """
        Delete tag.

        Args:
            tag_uuid: Tag UUID

        Returns:
            True if successful
        """
        await self._request("DELETE", f"/tags/{tag_uuid}")
        logger.info(f"Deleted tag: {tag_uuid}")
        return True

    # ========== Proxy Management ==========

    async def test_proxy(self, proxy: Proxy) -> Dict[str, Any]:
        """
        Test proxy connection.

        Args:
            proxy: Proxy object

        Returns:
            Test results with speed, location, etc.
        """
        data = await self._request("POST", "/proxy/test", json=proxy.to_dict())

        logger.info(f"Proxy test completed: {proxy.host}:{proxy.port}")
        return data

    async def import_proxies(self, proxies: List[Proxy]) -> Dict[str, Any]:
        """
        Import multiple proxies.

        Args:
            proxies: List of Proxy objects

        Returns:
            Import results
        """
        proxies_data = [p.to_dict() for p in proxies]
        data = await self._request("POST", "/proxies/import", json=proxies_data)

        logger.info(f"Imported {len(proxies)} proxies")
        return data

    # ========== Bulk Operations ==========

    async def bulk_create_profiles(self, profiles: List[Profile]) -> List[Profile]:
        """
        Create multiple profiles at once.

        Args:
            profiles: List of Profile objects

        Returns:
            List of created Profiles
        """
        profiles_data = [p.to_dict() for p in profiles]
        data = await self._request("POST", "/profiles/bulk", json=profiles_data)

        created = [Profile.from_dict(p) for p in data.get("data", [])]
        logger.info(f"Bulk created {len(created)} profiles")

        return created

    async def bulk_start_profiles(self, profile_uuids: List[str]) -> Dict[str, Any]:
        """
        Start multiple profiles at once.

        Args:
            profile_uuids: List of profile UUIDs

        Returns:
            Results for each profile
        """
        data = await self._request(
            "POST", "/profiles/bulk/start", json={"uuids": profile_uuids}
        )

        logger.info(f"Bulk started {len(profile_uuids)} profiles")
        return data

    async def bulk_stop_profiles(self, profile_uuids: List[str]) -> Dict[str, Any]:
        """
        Stop multiple profiles at once.

        Args:
            profile_uuids: List of profile UUIDs

        Returns:
            Results for each profile
        """
        data = await self._request(
            "POST", "/profiles/bulk/stop", json={"uuids": profile_uuids}
        )

        logger.info(f"Bulk stopped {len(profile_uuids)} profiles")
        return data

    async def bulk_delete_profiles(self, profile_uuids: List[str]) -> bool:
        """
        Delete multiple profiles at once.

        Args:
            profile_uuids: List of profile UUIDs

        Returns:
            True if successful
        """
        await self._request(
            "POST", "/profiles/bulk/delete", json={"uuids": profile_uuids}
        )

        logger.info(f"Bulk deleted {len(profile_uuids)} profiles")
        return True

    # ========== Statistics ==========

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get account statistics.

        Returns:
            Stats: total profiles, active profiles, tags, etc.
        """
        data = await self._request("GET", "/stats")
        logger.info("Retrieved account stats")
        return data

    # ========== Cleanup ==========

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("Octo Browser client closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def __repr__(self) -> str:
        return f"OctoClient(api_url={self.api_url})"
