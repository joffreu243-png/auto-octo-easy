"""
Mass operations module for Octo Browser.

Provides bulk operations combining profiles, proxies, and tags.
"""

from typing import List, Optional, Dict, Any, Callable
from loguru import logger

from src.octo.api import OctoAPI
from src.octo.profile_manager import ProfileManager
from src.octo.proxy_manager import ProxyManager
from src.octo.tag_manager import TagManager
from src.octo.models import (
    Profile,
    Proxy,
    Tag,
    ProfileCreateRequest,
    ProfileUpdateRequest,
    BrowserType,
    Fingerprint,
    BulkOperationResult,
)


class MassOperations:
    """Mass operations for profiles, proxies, and tags."""

    def __init__(
        self,
        api: OctoAPI,
        profile_manager: ProfileManager,
        proxy_manager: ProxyManager,
        tag_manager: TagManager,
    ):
        """Initialize mass operations.

        Args:
            api: OctoAPI instance
            profile_manager: ProfileManager instance
            proxy_manager: ProxyManager instance
            tag_manager: TagManager instance
        """
        self.api = api
        self.profiles = profile_manager
        self.proxies = proxy_manager
        self.tags = tag_manager

        logger.info("MassOperations initialized")

    async def assign_proxies_round_robin(
        self, profile_uuids: Optional[List[str]] = None, start_index: int = 0
    ) -> BulkOperationResult:
        """Assign proxies to profiles using round-robin strategy.

        Args:
            profile_uuids: List of profile UUIDs (None = all profiles)
            start_index: Starting proxy index

        Returns:
            Bulk operation result
        """
        # Get profiles
        if profile_uuids is None:
            profiles_list = await self.profiles.get_all_profiles()
            profile_uuids = [p.uuid for p in profiles_list]

        # Check if we have proxies
        if self.proxies.count() == 0:
            logger.error("No proxies available")
            return BulkOperationResult(
                total=len(profile_uuids), successful=0, failed=len(profile_uuids)
            )

        result = BulkOperationResult(total=0, successful=0, failed=0)

        # Assign proxies
        for i, uuid in enumerate(profile_uuids):
            try:
                # Get proxy using round-robin
                proxy = self.proxies.get_round_robin_proxy(start_index + i)

                if proxy:
                    # Update profile
                    request = ProfileUpdateRequest(uuid=uuid, proxy=proxy)
                    await self.api.update_profile(request)
                    result.add_success()

                    logger.debug(f"Assigned proxy to profile {i + 1}/{len(profile_uuids)}")
                else:
                    result.add_failure(uuid, "No proxy available")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(uuid, error_msg)
                logger.error(f"Failed to assign proxy to {uuid}: {error_msg}")

        logger.info(
            f"Round-robin proxy assignment: {result.successful}/{result.total} successful"
        )
        return result

    async def assign_tags_by_pattern(
        self,
        profile_uuids: List[str],
        tag_prefix: str,
        profiles_per_tag: int,
        tag_color: str = "#808080",
    ) -> BulkOperationResult:
        """Assign tags to profiles by pattern.

        Args:
            profile_uuids: List of profile UUIDs
            tag_prefix: Tag name prefix (e.g., "Group")
            profiles_per_tag: Number of profiles per tag
            tag_color: Tag color for new tags

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        # Calculate number of tags needed
        tag_count = (len(profile_uuids) + profiles_per_tag - 1) // profiles_per_tag

        # Create/get tags
        tags = await self.tags.find_or_create_by_pattern(
            tag_prefix, tag_count, tag_color
        )

        if not tags:
            logger.error("Failed to create tags")
            return result

        # Assign tags
        for i, uuid in enumerate(profile_uuids):
            try:
                # Get tag index
                tag_index = i // profiles_per_tag
                tag = tags[tag_index] if tag_index < len(tags) else tags[-1]

                # Get current profile
                profile = await self.api.get_profile(uuid, use_cache=False)

                # Add tag
                if not profile.has_tag(tag.uuid):
                    profile.add_tag(tag.uuid)

                    # Update profile
                    request = ProfileUpdateRequest(uuid=uuid, tags=profile.tags)
                    await self.api.update_profile(request)

                result.add_success()
                logger.debug(f"Assigned tag to profile {i + 1}/{len(profile_uuids)}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(uuid, error_msg)
                logger.error(f"Failed to assign tag to {uuid}: {error_msg}")

        logger.info(
            f"Pattern tag assignment: {result.successful}/{result.total} successful"
        )
        return result

    async def clone_profiles_with_proxies(
        self,
        source_uuid: str,
        count: int,
        title_pattern: str = "Profile {index}",
    ) -> BulkOperationResult:
        """Clone profile and assign different proxy to each clone.

        Args:
            source_uuid: Source profile UUID
            count: Number of clones
            title_pattern: Title pattern for clones

        Returns:
            Bulk operation result
        """
        # Check proxies
        if self.proxies.count() < count:
            logger.warning(
                f"Only {self.proxies.count()} proxies available for {count} clones"
            )

        # Get source profile
        try:
            source = await self.api.get_profile(source_uuid, use_cache=False)
        except Exception as e:
            logger.error(f"Failed to get source profile: {e}")
            result = BulkOperationResult(total=count, successful=0, failed=count)
            result.add_failure(source_uuid, str(e))
            return result

        result = BulkOperationResult(total=0, successful=0, failed=0)

        # Create clones
        for i in range(1, count + 1):
            try:
                # Generate title
                title = title_pattern.format(index=i, count=count)

                # Get proxy for this clone
                proxy = self.proxies.get_round_robin_proxy(i - 1)

                # Create request
                request = ProfileCreateRequest(
                    title=title,
                    description=source.description,
                    tags=source.tags.copy(),
                    proxy=proxy,  # Assign different proxy
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
            f"Clone with proxies: {result.successful}/{result.total} successful"
        )
        return result

    async def create_profiles_batch(
        self,
        count: int,
        title_pattern: str = "Profile {index}",
        assign_proxies: bool = True,
        assign_tags: Optional[List[str]] = None,
        browser_type: BrowserType = BrowserType.CHROME,
        fingerprint: Optional[Fingerprint] = None,
    ) -> BulkOperationResult:
        """Create batch of profiles with optional proxy/tag assignment.

        Args:
            count: Number of profiles to create
            title_pattern: Title pattern
            assign_proxies: Whether to assign proxies
            assign_tags: List of tag UUIDs to assign
            browser_type: Browser type
            fingerprint: Fingerprint configuration

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)
        assign_tags = assign_tags or []

        for i in range(1, count + 1):
            try:
                title = title_pattern.format(index=i, count=count)

                # Get proxy if needed
                proxy = None
                if assign_proxies and self.proxies.count() > 0:
                    proxy = self.proxies.get_round_robin_proxy(i - 1)

                # Create request
                request = ProfileCreateRequest(
                    title=title,
                    tags=assign_tags.copy(),
                    proxy=proxy,
                    fingerprint=fingerprint,
                    browser_type=browser_type,
                )

                await self.api.create_profile(request)
                result.add_success()

                logger.debug(f"Created profile {i}/{count}: {title}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(f"index_{i}", error_msg)
                logger.error(f"Failed to create profile {i}/{count}: {error_msg}")

        logger.info(f"Batch create: {result.successful}/{result.total} successful")
        return result

    async def update_profiles_by_tag(
        self, tag_uuid: str, updates: Dict[str, Any]
    ) -> BulkOperationResult:
        """Update all profiles with specific tag.

        Args:
            tag_uuid: Tag UUID
            updates: Fields to update

        Returns:
            Bulk operation result
        """
        # Get profiles with tag
        profiles_list = await self.profiles.filter_by_tag(tag_uuid)
        profile_uuids = [p.uuid for p in profiles_list]

        logger.info(f"Updating {len(profile_uuids)} profiles with tag {tag_uuid}")

        # Use bulk update
        return await self.profiles.bulk_update(profile_uuids, updates)

    async def delete_profiles_by_tag(self, tag_uuid: str) -> BulkOperationResult:
        """Delete all profiles with specific tag.

        Args:
            tag_uuid: Tag UUID

        Returns:
            Bulk operation result
        """
        # Get profiles with tag
        profiles_list = await self.profiles.filter_by_tag(tag_uuid)
        profile_uuids = [p.uuid for p in profiles_list]

        logger.info(f"Deleting {len(profile_uuids)} profiles with tag {tag_uuid}")

        # Use bulk delete
        return await self.profiles.bulk_delete(profile_uuids)

    async def rotate_proxies(
        self, profile_uuids: Optional[List[str]] = None
    ) -> BulkOperationResult:
        """Rotate proxies for profiles (assign next proxy in round-robin).

        Args:
            profile_uuids: List of profile UUIDs (None = all profiles with proxy)

        Returns:
            Bulk operation result
        """
        # Get profiles
        if profile_uuids is None:
            profiles_list = await self.profiles.get_profiles_with_proxy()
            profile_uuids = [p.uuid for p in profiles_list]

        # Check proxies
        if self.proxies.count() == 0:
            logger.error("No proxies available for rotation")
            return BulkOperationResult(
                total=len(profile_uuids), successful=0, failed=len(profile_uuids)
            )

        result = BulkOperationResult(total=0, successful=0, failed=0)

        # Rotate proxies (shift by 1)
        for i, uuid in enumerate(profile_uuids):
            try:
                # Get next proxy (offset by total count to rotate)
                proxy = self.proxies.get_round_robin_proxy(i + len(profile_uuids))

                if proxy:
                    request = ProfileUpdateRequest(uuid=uuid, proxy=proxy)
                    await self.api.update_profile(request)
                    result.add_success()

                    logger.debug(f"Rotated proxy for profile {i + 1}/{len(profile_uuids)}")
                else:
                    result.add_failure(uuid, "No proxy available")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(uuid, error_msg)
                logger.error(f"Failed to rotate proxy for {uuid}: {error_msg}")

        logger.info(f"Proxy rotation: {result.successful}/{result.total} successful")
        return result

    async def migrate_tag(
        self, from_tag_uuid: str, to_tag_uuid: str, delete_old_tag: bool = False
    ) -> BulkOperationResult:
        """Migrate profiles from one tag to another.

        Args:
            from_tag_uuid: Source tag UUID
            to_tag_uuid: Destination tag UUID
            delete_old_tag: Whether to delete old tag after migration

        Returns:
            Bulk operation result
        """
        # Get profiles with source tag
        profiles_list = await self.profiles.filter_by_tag(from_tag_uuid)

        result = BulkOperationResult(total=0, successful=0, failed=0)

        for profile in profiles_list:
            try:
                # Remove old tag
                profile.remove_tag(from_tag_uuid)

                # Add new tag
                profile.add_tag(to_tag_uuid)

                # Update profile
                request = ProfileUpdateRequest(uuid=profile.uuid, tags=profile.tags)
                await self.api.update_profile(request)

                result.add_success()
                logger.debug(f"Migrated profile {profile.uuid}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(profile.uuid, error_msg)
                logger.error(f"Failed to migrate profile {profile.uuid}: {error_msg}")

        # Delete old tag if requested
        if delete_old_tag and result.successful > 0:
            try:
                await self.tags.delete_tag(from_tag_uuid)
                logger.info(f"Deleted old tag: {from_tag_uuid}")
            except Exception as e:
                logger.warning(f"Failed to delete old tag: {e}")

        logger.info(f"Tag migration: {result.successful}/{result.total} successful")
        return result

    async def cleanup_profiles_without_proxy(self) -> BulkOperationResult:
        """Delete all profiles that don't have proxy assigned.

        Returns:
            Bulk operation result
        """
        # Get profiles without proxy
        profiles_list = await self.profiles.get_profiles_without_proxy()
        profile_uuids = [p.uuid for p in profiles_list]

        logger.info(f"Cleaning up {len(profile_uuids)} profiles without proxy")

        # Use bulk delete
        return await self.profiles.bulk_delete(profile_uuids)

    async def apply_operation_to_filtered(
        self,
        filter_func: Callable[[Profile], bool],
        operation: Callable[[str], Any],
    ) -> BulkOperationResult:
        """Apply custom operation to filtered profiles.

        Args:
            filter_func: Function to filter profiles
            operation: Async function to apply (receives profile UUID)

        Returns:
            Bulk operation result
        """
        # Get filtered profiles
        profiles_list = await self.profiles.filter_profiles(filter_func)

        result = BulkOperationResult(total=0, successful=0, failed=0)

        for profile in profiles_list:
            try:
                await operation(profile.uuid)
                result.add_success()
                logger.debug(f"Applied operation to profile {profile.uuid}")

            except Exception as e:
                error_msg = str(e)
                result.add_failure(profile.uuid, error_msg)
                logger.error(f"Failed to apply operation to {profile.uuid}: {error_msg}")

        logger.info(
            f"Custom operation: {result.successful}/{result.total} successful"
        )
        return result
