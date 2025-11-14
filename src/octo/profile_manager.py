"""
Profile management module for Octo Browser.

Provides high-level profile operations including search, filtering, and bulk operations.
"""

from typing import List, Optional, Dict, Any, Callable
from loguru import logger

from src.octo.api import OctoAPI
from src.octo.models import (
    Profile,
    ProfileCreateRequest,
    ProfileUpdateRequest,
    ProfileStatus,
    BrowserType,
    Proxy,
    Fingerprint,
    BulkOperationResult,
)


class ProfileManager:
    """High-level profile management."""

    def __init__(self, api: OctoAPI):
        """Initialize profile manager.

        Args:
            api: OctoAPI instance
        """
        self.api = api
        logger.info("ProfileManager initialized")

    async def get_all_profiles(
        self, use_cache: bool = False, limit_per_page: int = 100
    ) -> List[Profile]:
        """Get all profiles with automatic pagination.

        Args:
            use_cache: Whether to use cache
            limit_per_page: Results per page

        Returns:
            List of all profiles
        """
        all_profiles: List[Profile] = []
        page = 1

        while True:
            response = await self.api.get_profiles(
                page=page, limit=limit_per_page, use_cache=use_cache
            )

            if "data" not in response or not response["data"]:
                break

            profiles = [Profile.from_dict(p) for p in response["data"]]
            all_profiles.extend(profiles)

            # Check if there are more pages
            total = response.get("total", 0)
            if len(all_profiles) >= total:
                break

            page += 1
            logger.debug(f"Fetched page {page}, total profiles: {len(all_profiles)}")

        logger.info(f"Retrieved {len(all_profiles)} total profiles")
        return all_profiles

    async def search_profiles(
        self, field: str, value: Any, exact_match: bool = False
    ) -> List[Profile]:
        """Search profiles by field value.

        Args:
            field: Field to search (title, description, notes)
            value: Value to search for
            exact_match: Exact match or contains

        Returns:
            Matching profiles
        """
        all_profiles = await self.get_all_profiles()
        results: List[Profile] = []

        for profile in all_profiles:
            field_value = getattr(profile, field, None)

            if field_value is None:
                continue

            # Convert to string for comparison
            field_str = str(field_value).lower()
            search_str = str(value).lower()

            if exact_match:
                if field_str == search_str:
                    results.append(profile)
            else:
                if search_str in field_str:
                    results.append(profile)

        logger.info(
            f"Found {len(results)} profiles matching {field}='{value}' "
            f"(exact={exact_match})"
        )
        return results

    async def filter_profiles(
        self, filter_func: Callable[[Profile], bool]
    ) -> List[Profile]:
        """Filter profiles with custom function.

        Args:
            filter_func: Function that returns True for matching profiles

        Returns:
            Filtered profiles
        """
        all_profiles = await self.get_all_profiles()
        results = [p for p in all_profiles if filter_func(p)]

        logger.info(f"Filtered {len(results)} profiles from {len(all_profiles)} total")
        return results

    async def filter_by_tag(self, tag_uuid: str) -> List[Profile]:
        """Get profiles with specific tag.

        Args:
            tag_uuid: Tag UUID

        Returns:
            Profiles with tag
        """
        return await self.filter_profiles(lambda p: p.has_tag(tag_uuid))

    async def filter_by_status(self, status: ProfileStatus) -> List[Profile]:
        """Get profiles with specific status.

        Args:
            status: Profile status

        Returns:
            Profiles with status
        """
        return await self.filter_profiles(lambda p: p.status == status)

    async def filter_by_browser_type(self, browser_type: BrowserType) -> List[Profile]:
        """Get profiles with specific browser type.

        Args:
            browser_type: Browser type

        Returns:
            Profiles with browser type
        """
        return await self.filter_profiles(lambda p: p.browser_type == browser_type)

    async def get_profiles_with_proxy(self) -> List[Profile]:
        """Get profiles that have proxy configured.

        Returns:
            Profiles with proxy
        """
        return await self.filter_profiles(lambda p: p.proxy is not None)

    async def get_profiles_without_proxy(self) -> List[Profile]:
        """Get profiles that don't have proxy configured.

        Returns:
            Profiles without proxy
        """
        return await self.filter_profiles(lambda p: p.proxy is None)

    async def bulk_create(
        self,
        count: int,
        title_pattern: str = "Profile {index}",
        description: str = "",
        tags: Optional[List[str]] = None,
        proxy: Optional[Proxy] = None,
        fingerprint: Optional[Fingerprint] = None,
        browser_type: BrowserType = BrowserType.CHROME,
        start_url: str = "about:blank",
    ) -> BulkOperationResult:
        """Create multiple profiles with name pattern.

        Args:
            count: Number of profiles to create
            title_pattern: Title pattern with {index} placeholder
            description: Profile description
            tags: List of tag UUIDs
            proxy: Proxy configuration (same for all)
            fingerprint: Fingerprint configuration (same for all)
            browser_type: Browser type
            start_url: Start URL

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)
        tags = tags or []

        for i in range(1, count + 1):
            try:
                title = title_pattern.format(index=i, count=count)

                request = ProfileCreateRequest(
                    title=title,
                    description=description,
                    tags=tags.copy(),
                    proxy=proxy,
                    fingerprint=fingerprint,
                    browser_type=browser_type,
                    start_url=start_url,
                )

                await self.api.create_profile(request)
                result.add_success()

                logger.debug(f"Created profile {i}/{count}: {title}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(f"index_{i}", error_msg)
                logger.error(f"Failed to create profile {i}/{count}: {error_msg}")

        logger.info(
            f"Bulk create completed: {result.successful}/{result.total} successful"
        )
        return result

    async def bulk_update(
        self,
        profile_uuids: List[str],
        updates: Dict[str, Any],
    ) -> BulkOperationResult:
        """Update multiple profiles.

        Args:
            profile_uuids: List of profile UUIDs
            updates: Fields to update (title, description, tags, etc.)

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        for uuid in profile_uuids:
            try:
                request = ProfileUpdateRequest(uuid=uuid, **updates)
                await self.api.update_profile(request)
                result.add_success()

                logger.debug(f"Updated profile: {uuid}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(uuid, error_msg)
                logger.error(f"Failed to update profile {uuid}: {error_msg}")

        logger.info(
            f"Bulk update completed: {result.successful}/{result.total} successful"
        )
        return result

    async def bulk_delete(self, profile_uuids: List[str]) -> BulkOperationResult:
        """Delete multiple profiles.

        Args:
            profile_uuids: List of profile UUIDs

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        for uuid in profile_uuids:
            try:
                await self.api.delete_profile(uuid)
                result.add_success()

                logger.debug(f"Deleted profile: {uuid}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(uuid, error_msg)
                logger.error(f"Failed to delete profile {uuid}: {error_msg}")

        logger.info(
            f"Bulk delete completed: {result.successful}/{result.total} successful"
        )
        return result

    async def bulk_add_tag(
        self, profile_uuids: List[str], tag_uuid: str
    ) -> BulkOperationResult:
        """Add tag to multiple profiles.

        Args:
            profile_uuids: List of profile UUIDs
            tag_uuid: Tag UUID to add

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        for uuid in profile_uuids:
            try:
                # Get current profile
                profile = await self.api.get_profile(uuid, use_cache=False)

                # Add tag if not already present
                if not profile.has_tag(tag_uuid):
                    profile.add_tag(tag_uuid)

                    # Update profile
                    request = ProfileUpdateRequest(uuid=uuid, tags=profile.tags)
                    await self.api.update_profile(request)

                result.add_success()
                logger.debug(f"Added tag to profile: {uuid}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(uuid, error_msg)
                logger.error(f"Failed to add tag to profile {uuid}: {error_msg}")

        logger.info(
            f"Bulk add tag completed: {result.successful}/{result.total} successful"
        )
        return result

    async def bulk_remove_tag(
        self, profile_uuids: List[str], tag_uuid: str
    ) -> BulkOperationResult:
        """Remove tag from multiple profiles.

        Args:
            profile_uuids: List of profile UUIDs
            tag_uuid: Tag UUID to remove

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        for uuid in profile_uuids:
            try:
                # Get current profile
                profile = await self.api.get_profile(uuid, use_cache=False)

                # Remove tag if present
                if profile.has_tag(tag_uuid):
                    profile.remove_tag(tag_uuid)

                    # Update profile
                    request = ProfileUpdateRequest(uuid=uuid, tags=profile.tags)
                    await self.api.update_profile(request)

                result.add_success()
                logger.debug(f"Removed tag from profile: {uuid}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(uuid, error_msg)
                logger.error(f"Failed to remove tag from profile {uuid}: {error_msg}")

        logger.info(
            f"Bulk remove tag completed: {result.successful}/{result.total} successful"
        )
        return result

    async def bulk_assign_proxy(
        self, profile_uuids: List[str], proxy: Proxy
    ) -> BulkOperationResult:
        """Assign proxy to multiple profiles.

        Args:
            profile_uuids: List of profile UUIDs
            proxy: Proxy to assign

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        for uuid in profile_uuids:
            try:
                request = ProfileUpdateRequest(uuid=uuid, proxy=proxy)
                await self.api.update_profile(request)
                result.add_success()

                logger.debug(f"Assigned proxy to profile: {uuid}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(uuid, error_msg)
                logger.error(f"Failed to assign proxy to profile {uuid}: {error_msg}")

        logger.info(
            f"Bulk assign proxy completed: {result.successful}/{result.total} successful"
        )
        return result

    async def bulk_start(self, profile_uuids: List[str]) -> BulkOperationResult:
        """Start multiple profiles.

        Args:
            profile_uuids: List of profile UUIDs

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        for uuid in profile_uuids:
            try:
                await self.api.start_profile(uuid)
                result.add_success()

                logger.debug(f"Started profile: {uuid}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(uuid, error_msg)
                logger.error(f"Failed to start profile {uuid}: {error_msg}")

        logger.info(
            f"Bulk start completed: {result.successful}/{result.total} successful"
        )
        return result

    async def bulk_stop(self, profile_uuids: List[str]) -> BulkOperationResult:
        """Stop multiple profiles.

        Args:
            profile_uuids: List of profile UUIDs

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        for uuid in profile_uuids:
            try:
                await self.api.stop_profile(uuid)
                result.add_success()

                logger.debug(f"Stopped profile: {uuid}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(uuid, error_msg)
                logger.error(f"Failed to stop profile {uuid}: {error_msg}")

        logger.info(
            f"Bulk stop completed: {result.successful}/{result.total} successful"
        )
        return result

    async def get_statistics(self) -> Dict[str, Any]:
        """Get profile statistics.

        Returns:
            Statistics dictionary
        """
        all_profiles = await self.get_all_profiles()

        # Count by status
        status_counts: Dict[str, int] = {}
        for status in ProfileStatus:
            count = sum(1 for p in all_profiles if p.status == status)
            status_counts[status.name] = count

        # Count by browser type
        browser_counts: Dict[str, int] = {}
        for browser in BrowserType:
            count = sum(1 for p in all_profiles if p.browser_type == browser)
            browser_counts[browser.name] = count

        # Count with/without proxy
        with_proxy = sum(1 for p in all_profiles if p.proxy is not None)
        without_proxy = len(all_profiles) - with_proxy

        # Tag usage
        tag_usage: Dict[str, int] = {}
        for profile in all_profiles:
            for tag_uuid in profile.tags:
                tag_usage[tag_uuid] = tag_usage.get(tag_uuid, 0) + 1

        return {
            "total_profiles": len(all_profiles),
            "by_status": status_counts,
            "by_browser_type": browser_counts,
            "with_proxy": with_proxy,
            "without_proxy": without_proxy,
            "tag_usage": tag_usage,
            "most_used_tags": sorted(
                tag_usage.items(), key=lambda x: x[1], reverse=True
            )[:10],
        }

    async def clone_profile(
        self, source_uuid: str, new_title: Optional[str] = None, count: int = 1
    ) -> BulkOperationResult:
        """Clone profile(s).

        Args:
            source_uuid: Source profile UUID
            new_title: Title for cloned profile(s) (supports {index})
            count: Number of clones to create

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        # Get source profile
        try:
            source = await self.api.get_profile(source_uuid, use_cache=False)
        except Exception as e:
            logger.error(f"Failed to get source profile: {e}")
            result.add_failure(source_uuid, str(e))
            return result

        # Create clones
        for i in range(1, count + 1):
            try:
                title = (
                    new_title.format(index=i, count=count)
                    if new_title
                    else f"{source.title} (Copy {i})"
                )

                request = ProfileCreateRequest(
                    title=title,
                    description=source.description,
                    tags=source.tags.copy(),
                    proxy=source.proxy,
                    fingerprint=source.fingerprint,
                    browser_type=source.browser_type,
                    start_url=source.start_url,
                )

                await self.api.create_profile(request)
                result.add_success()

                logger.debug(f"Cloned profile {i}/{count}: {title}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(f"clone_{i}", error_msg)
                logger.error(f"Failed to clone profile {i}/{count}: {error_msg}")

        logger.info(
            f"Clone profile completed: {result.successful}/{result.total} successful"
        )
        return result
