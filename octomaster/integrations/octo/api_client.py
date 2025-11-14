"""
Octo Browser API Client.

Provides integration with Octo Browser Local API for profile management
and automation.
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
from dataclasses import dataclass


@dataclass
class OctoProfile:
    """Octo Browser profile information."""

    uuid: str
    title: str
    tags: List[str] = None
    proxy: Dict[str, Any] = None
    fingerprint: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.proxy is None:
            self.proxy = {}
        if self.fingerprint is None:
            self.fingerprint = {}


@dataclass
class OctoStartResult:
    """Result of starting an Octo profile."""

    uuid: str
    ws_endpoint: str
    debug_port: int
    selenium_port: Optional[int] = None


class OctoAPIClient:
    """Client for Octo Browser Local API.

    Connects to Octo Browser running locally and provides methods to:
    - List profiles
    - Create profiles
    - Start/stop profiles
    - Get profile details
    """

    def __init__(self, api_token: str, base_url: str = "http://localhost:58888"):
        """Initialize Octo API client.

        Args:
            api_token: Octo Browser API token
            base_url: Base URL for Local API (default: http://localhost:58888)
        """
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)

        logger.info(f"OctoAPIClient initialized with base_url: {self.base_url}")

    def _headers(self) -> Dict[str, str]:
        """Get request headers with API token."""
        return {
            "X-Octo-Api-Token": self.api_token,
            "Content-Type": "application/json"
        }

    async def check_connection(self) -> bool:
        """Check if Octo Browser is running and API token is valid.

        Returns:
            True if connection successful
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/profiles",
                headers=self._headers()
            )

            if response.status_code == 200:
                logger.info("✅ Octo Browser API connection successful")
                return True
            elif response.status_code == 401:
                logger.error("❌ Invalid API token")
                return False
            else:
                logger.error(f"❌ Unexpected status code: {response.status_code}")
                return False

        except httpx.ConnectError:
            logger.error("❌ Cannot connect to Octo Browser. Is it running?")
            return False
        except Exception as e:
            logger.error(f"❌ Connection check failed: {e}")
            return False

    async def list_profiles(self, tags: Optional[List[str]] = None) -> List[OctoProfile]:
        """Get list of profiles.

        Args:
            tags: Filter by tags (optional)

        Returns:
            List of profiles
        """
        try:
            url = f"{self.base_url}/api/profiles"

            # Add tags filter if provided
            params = {}
            if tags:
                params['tags'] = ','.join(tags)

            response = await self.client.get(
                url,
                headers=self._headers(),
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                profiles = []

                for item in data.get('data', []):
                    profile = OctoProfile(
                        uuid=item.get('uuid', ''),
                        title=item.get('title', 'Untitled'),
                        tags=item.get('tags', []),
                        proxy=item.get('proxy', {}),
                        fingerprint=item.get('fingerprint', {})
                    )
                    profiles.append(profile)

                logger.info(f"📋 Found {len(profiles)} profiles")
                return profiles
            else:
                logger.error(f"Failed to get profiles: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error listing profiles: {e}")
            return []

    async def get_profile(self, profile_uuid: str) -> Optional[OctoProfile]:
        """Get profile details by UUID.

        Args:
            profile_uuid: Profile UUID

        Returns:
            Profile info or None
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/profiles/{profile_uuid}",
                headers=self._headers()
            )

            if response.status_code == 200:
                data = response.json().get('data', {})

                profile = OctoProfile(
                    uuid=data.get('uuid', ''),
                    title=data.get('title', 'Untitled'),
                    tags=data.get('tags', []),
                    proxy=data.get('proxy', {}),
                    fingerprint=data.get('fingerprint', {})
                )

                logger.info(f"📄 Got profile: {profile.title}")
                return profile
            else:
                logger.error(f"Failed to get profile: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return None

    async def start_profile(
        self,
        profile_uuid: str,
        debug_port: Optional[int] = None,
        headless: bool = False
    ) -> Optional[OctoStartResult]:
        """Start an Octo profile.

        Args:
            profile_uuid: Profile UUID to start
            debug_port: Custom debug port (optional, auto-assigned if not specified)
            headless: Start in headless mode

        Returns:
            Start result with connection info
        """
        try:
            payload = {
                "uuid": profile_uuid
            }

            if debug_port:
                payload["debug_port"] = debug_port

            if headless:
                payload["headless"] = True

            logger.info(f"🚀 Starting profile: {profile_uuid}")

            response = await self.client.post(
                f"{self.base_url}/api/profiles/start",
                headers=self._headers(),
                json=payload
            )

            if response.status_code == 200:
                data = response.json().get('data', {})

                result = OctoStartResult(
                    uuid=data.get('uuid', profile_uuid),
                    ws_endpoint=data.get('ws_endpoint', ''),
                    debug_port=data.get('debug_port', 0),
                    selenium_port=data.get('selenium_port')
                )

                logger.info(f"✅ Profile started on port {result.debug_port}")
                logger.debug(f"WebSocket: {result.ws_endpoint}")

                return result
            else:
                error_msg = response.json().get('message', 'Unknown error')
                logger.error(f"❌ Failed to start profile: {error_msg}")
                return None

        except Exception as e:
            logger.error(f"Error starting profile: {e}")
            return None

    async def stop_profile(self, profile_uuid: str) -> bool:
        """Stop a running profile.

        Args:
            profile_uuid: Profile UUID to stop

        Returns:
            True if stopped successfully
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/profiles/stop",
                headers=self._headers(),
                json={"uuid": profile_uuid}
            )

            if response.status_code == 200:
                logger.info(f"⏹️ Profile stopped: {profile_uuid}")
                return True
            else:
                logger.error(f"Failed to stop profile: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error stopping profile: {e}")
            return False

    async def create_profile(
        self,
        title: str,
        tags: Optional[List[str]] = None,
        proxy: Optional[Dict[str, Any]] = None,
        fingerprint: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[str]:
        """Create a new profile.

        Args:
            title: Profile title/name
            tags: Profile tags
            proxy: Proxy configuration
            fingerprint: Fingerprint settings
            **kwargs: Additional profile parameters

        Returns:
            Created profile UUID or None
        """
        try:
            payload = {
                "title": title,
                "tags": tags or [],
                **kwargs
            }

            if proxy:
                payload["proxy"] = proxy

            if fingerprint:
                payload["fingerprint"] = fingerprint

            response = await self.client.post(
                f"{self.base_url}/api/profiles",
                headers=self._headers(),
                json=payload
            )

            if response.status_code == 200:
                data = response.json().get('data', {})
                uuid = data.get('uuid', '')
                logger.info(f"✅ Profile created: {title} ({uuid})")
                return uuid
            else:
                logger.error(f"Failed to create profile: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            return None

    async def delete_profile(self, profile_uuid: str) -> bool:
        """Delete a profile.

        Args:
            profile_uuid: Profile UUID to delete

        Returns:
            True if deleted successfully
        """
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/profiles/{profile_uuid}",
                headers=self._headers()
            )

            if response.status_code == 200:
                logger.info(f"🗑️ Profile deleted: {profile_uuid}")
                return True
            else:
                logger.error(f"Failed to delete profile: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error deleting profile: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.debug("OctoAPIClient closed")
