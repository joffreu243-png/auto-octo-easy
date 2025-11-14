"""
Enhanced Octo Browser API wrapper.

Provides comprehensive API client with rate limiting, caching, and retry logic.
"""

from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime, timedelta
import time
from loguru import logger
import httpx

from src.octo.models import Profile, Tag, Proxy, ProfileCreateRequest, ProfileUpdateRequest


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, requests_per_minute: int = 50, requests_per_hour: int = 500):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Max requests per minute
            requests_per_hour: Max requests per hour
        """
        self.rpm_limit = requests_per_minute
        self.rph_limit = requests_per_hour

        # Minute window
        self.minute_requests: List[float] = []

        # Hour window
        self.hour_requests: List[float] = []

    async def acquire(self) -> None:
        """Acquire permission to make request (blocks if rate limit exceeded)."""
        now = time.time()

        # Clean old requests
        self._clean_old_requests(now)

        # Check minute limit
        while len(self.minute_requests) >= self.rpm_limit:
            await asyncio.sleep(0.1)
            now = time.time()
            self._clean_old_requests(now)

        # Check hour limit
        while len(self.hour_requests) >= self.rph_limit:
            await asyncio.sleep(1)
            now = time.time()
            self._clean_old_requests(now)

        # Record request
        self.minute_requests.append(now)
        self.hour_requests.append(now)

    def _clean_old_requests(self, now: float) -> None:
        """Remove old requests outside time windows.

        Args:
            now: Current timestamp
        """
        # Remove minute-old requests
        minute_ago = now - 60
        self.minute_requests = [t for t in self.minute_requests if t > minute_ago]

        # Remove hour-old requests
        hour_ago = now - 3600
        self.hour_requests = [t for t in self.hour_requests if t > hour_ago]


class ResponseCache:
    """Simple response cache with TTL."""

    def __init__(self, default_ttl: int = 60):
        """Initialize cache.

        Args:
            default_ttl: Default TTL in seconds
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if key not in self.cache:
            return None

        entry = self.cache[key]
        expires_at = entry["expires_at"]

        if datetime.now() > expires_at:
            # Expired
            del self.cache[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value.

        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (uses default if not provided)
        """
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)

        self.cache[key] = {"value": value, "expires_at": expires_at}

    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()

    def invalidate(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern.

        Args:
            pattern: Pattern to match (simple string contains)
        """
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.cache[key]


class OctoAPI:
    """Enhanced Octo Browser API client."""

    def __init__(
        self,
        api_token: str,
        base_url: str = "https://app.octobrowser.net/api/v2/automation",
        requests_per_minute: int = 50,
        requests_per_hour: int = 500,
        cache_ttl: int = 60,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize API client.

        Args:
            api_token: Octo Browser API token
            base_url: API base URL
            requests_per_minute: Rate limit per minute
            requests_per_hour: Rate limit per hour
            cache_ttl: Cache TTL in seconds
            max_retries: Maximum retry attempts
            retry_delay: Initial retry delay in seconds
        """
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Rate limiting
        self.rate_limiter = RateLimiter(requests_per_minute, requests_per_hour)

        # Caching
        self.cache = ResponseCache(cache_ttl)

        # HTTP client
        self.client = httpx.AsyncClient(
            headers={
                "X-API-TOKEN": api_token,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        logger.info("OctoAPI initialized")

    async def close(self) -> None:
        """Close API client."""
        await self.client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        use_cache: bool = False,
        cache_ttl: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make API request with rate limiting and retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            use_cache: Whether to use cache for GET requests
            cache_ttl: Custom cache TTL

        Returns:
            Response data

        Raises:
            Exception: If request fails after retries
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Check cache for GET requests
        if method == "GET" and use_cache:
            cache_key = f"{method}:{url}"
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached

        # Rate limiting
        await self.rate_limiter.acquire()

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    response = await self.client.get(url)
                elif method == "POST":
                    response = await self.client.post(url, json=data)
                elif method == "PATCH":
                    response = await self.client.patch(url, json=data)
                elif method == "DELETE":
                    response = await self.client.delete(url)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                # Check response
                response.raise_for_status()

                result = response.json()

                # Cache successful GET requests
                if method == "GET" and use_cache:
                    cache_key = f"{method}:{url}"
                    self.cache.set(cache_key, result, cache_ttl)

                logger.debug(f"API {method} {endpoint}: success")
                return result

            except httpx.HTTPStatusError as e:
                last_error = e
                status_code = e.response.status_code

                # Don't retry on client errors (4xx)
                if 400 <= status_code < 500:
                    logger.error(f"API {method} {endpoint}: {status_code} - {e}")
                    raise

                # Retry on server errors (5xx)
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)  # Exponential backoff
                    logger.warning(
                        f"API {method} {endpoint}: {status_code}, "
                        f"retrying in {delay}s (attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"API {method} {endpoint}: failed after {self.max_retries} attempts")
                    raise

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)
                    logger.warning(
                        f"API {method} {endpoint}: {e}, "
                        f"retrying in {delay}s (attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"API {method} {endpoint}: failed after {self.max_retries} attempts")
                    raise

        # Should not reach here, but just in case
        raise last_error or Exception("Request failed")

    # ========== Profile Endpoints ==========

    async def get_profiles(
        self, page: int = 1, limit: int = 50, use_cache: bool = True
    ) -> Dict[str, Any]:
        """Get profiles list.

        Args:
            page: Page number
            limit: Results per page
            use_cache: Whether to use cache

        Returns:
            Response with profiles list
        """
        endpoint = f"profiles?page={page}&limit={limit}"
        return await self._request("GET", endpoint, use_cache=use_cache, cache_ttl=30)

    async def get_profile(self, profile_uuid: str, use_cache: bool = True) -> Profile:
        """Get profile by UUID.

        Args:
            profile_uuid: Profile UUID
            use_cache: Whether to use cache

        Returns:
            Profile instance

        Raises:
            Exception: If profile not found
        """
        endpoint = f"profiles/{profile_uuid}"
        response = await self._request("GET", endpoint, use_cache=use_cache)

        if "data" not in response:
            raise Exception(f"Profile not found: {profile_uuid}")

        return Profile.from_dict(response["data"])

    async def create_profile(self, request: ProfileCreateRequest) -> Profile:
        """Create new profile.

        Args:
            request: Profile creation request

        Returns:
            Created profile

        Raises:
            Exception: If creation fails
        """
        response = await self._request("POST", "profiles", data=request.to_dict())

        # Invalidate profiles cache
        self.cache.invalidate("profiles")

        if "data" not in response:
            raise Exception("Failed to create profile")

        return Profile.from_dict(response["data"])

    async def update_profile(self, request: ProfileUpdateRequest) -> Profile:
        """Update profile.

        Args:
            request: Profile update request

        Returns:
            Updated profile

        Raises:
            Exception: If update fails
        """
        endpoint = f"profiles/{request.uuid}"
        response = await self._request("PATCH", endpoint, data=request.to_dict())

        # Invalidate cache
        self.cache.invalidate(f"profiles/{request.uuid}")
        self.cache.invalidate("profiles?")

        if "data" not in response:
            raise Exception(f"Failed to update profile: {request.uuid}")

        return Profile.from_dict(response["data"])

    async def delete_profile(self, profile_uuid: str) -> bool:
        """Delete profile.

        Args:
            profile_uuid: Profile UUID

        Returns:
            True if successful

        Raises:
            Exception: If deletion fails
        """
        endpoint = f"profiles/{profile_uuid}"
        await self._request("DELETE", endpoint)

        # Invalidate cache
        self.cache.invalidate(f"profiles/{profile_uuid}")
        self.cache.invalidate("profiles?")

        logger.info(f"Profile deleted: {profile_uuid}")
        return True

    async def start_profile(self, profile_uuid: str) -> Dict[str, Any]:
        """Start profile (launch browser).

        Args:
            profile_uuid: Profile UUID

        Returns:
            Start response with WebSocket URL and port

        Raises:
            Exception: If start fails
        """
        endpoint = f"profiles/{profile_uuid}/start"
        response = await self._request("POST", endpoint)

        logger.info(f"Profile started: {profile_uuid}")
        return response

    async def stop_profile(self, profile_uuid: str) -> bool:
        """Stop profile (close browser).

        Args:
            profile_uuid: Profile UUID

        Returns:
            True if successful

        Raises:
            Exception: If stop fails
        """
        endpoint = f"profiles/{profile_uuid}/stop"
        await self._request("POST", endpoint)

        logger.info(f"Profile stopped: {profile_uuid}")
        return True

    # ========== Tag Endpoints ==========

    async def get_tags(self, use_cache: bool = True) -> List[Tag]:
        """Get all tags.

        Args:
            use_cache: Whether to use cache

        Returns:
            List of tags
        """
        response = await self._request("GET", "tags", use_cache=use_cache, cache_ttl=120)

        if "data" not in response:
            return []

        return [Tag.from_dict(tag_data) for tag_data in response["data"]]

    async def create_tag(self, name: str, color: str = "#808080") -> Tag:
        """Create new tag.

        Args:
            name: Tag name
            color: Tag color (hex)

        Returns:
            Created tag

        Raises:
            Exception: If creation fails
        """
        data = {"name": name, "color": color}
        response = await self._request("POST", "tags", data=data)

        # Invalidate cache
        self.cache.invalidate("tags")

        if "data" not in response:
            raise Exception("Failed to create tag")

        return Tag.from_dict(response["data"])

    async def update_tag(self, tag_uuid: str, name: Optional[str] = None, color: Optional[str] = None) -> Tag:
        """Update tag.

        Args:
            tag_uuid: Tag UUID
            name: New name (optional)
            color: New color (optional)

        Returns:
            Updated tag

        Raises:
            Exception: If update fails
        """
        data = {}
        if name is not None:
            data["name"] = name
        if color is not None:
            data["color"] = color

        endpoint = f"tags/{tag_uuid}"
        response = await self._request("PATCH", endpoint, data=data)

        # Invalidate cache
        self.cache.invalidate("tags")

        if "data" not in response:
            raise Exception(f"Failed to update tag: {tag_uuid}")

        return Tag.from_dict(response["data"])

    async def delete_tag(self, tag_uuid: str) -> bool:
        """Delete tag.

        Args:
            tag_uuid: Tag UUID

        Returns:
            True if successful

        Raises:
            Exception: If deletion fails
        """
        endpoint = f"tags/{tag_uuid}"
        await self._request("DELETE", endpoint)

        # Invalidate cache
        self.cache.invalidate("tags")

        logger.info(f"Tag deleted: {tag_uuid}")
        return True

    # ========== Utility Methods ==========

    async def get_all_profiles(self, limit_per_page: int = 100) -> List[Profile]:
        """Get all profiles with automatic pagination.

        Args:
            limit_per_page: Results per page

        Returns:
            List of all profiles
        """
        all_profiles: List[Profile] = []
        page = 1

        while True:
            response = await self.get_profiles(page=page, limit=limit_per_page)

            if "data" not in response or not response["data"]:
                break

            profiles = [Profile.from_dict(p) for p in response["data"]]
            all_profiles.extend(profiles)

            # Check if there are more pages
            total = response.get("total", 0)
            if len(all_profiles) >= total:
                break

            page += 1

        logger.info(f"Retrieved {len(all_profiles)} total profiles")
        return all_profiles

    async def bulk_delete_profiles(self, profile_uuids: List[str]) -> Dict[str, int]:
        """Delete multiple profiles.

        Args:
            profile_uuids: List of profile UUIDs

        Returns:
            Statistics: successful, failed counts
        """
        successful = 0
        failed = 0

        for uuid in profile_uuids:
            try:
                await self.delete_profile(uuid)
                successful += 1
            except Exception as e:
                logger.error(f"Failed to delete profile {uuid}: {e}")
                failed += 1

        return {"successful": successful, "failed": failed, "total": len(profile_uuids)}

    def clear_cache(self) -> None:
        """Clear all cached responses."""
        self.cache.clear()
        logger.info("API cache cleared")
