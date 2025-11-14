"""
Import/export module for Octo Browser profiles.

Provides functionality to import and export profiles in various formats.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import csv
from loguru import logger

from src.octo.api import OctoAPI
from src.octo.profile_manager import ProfileManager
from src.octo.models import (
    Profile,
    ProfileCreateRequest,
    Proxy,
    Fingerprint,
    BrowserType,
    BulkOperationResult,
)


class ProfileImportExport:
    """Import and export profiles."""

    def __init__(self, api: OctoAPI, profile_manager: ProfileManager):
        """Initialize import/export.

        Args:
            api: OctoAPI instance
            profile_manager: ProfileManager instance
        """
        self.api = api
        self.profiles = profile_manager
        logger.info("ProfileImportExport initialized")

    async def export_to_json(
        self, file_path: Path, profile_uuids: Optional[List[str]] = None
    ) -> bool:
        """Export profiles to JSON file.

        Args:
            file_path: Output file path
            profile_uuids: List of profile UUIDs (None = all profiles)

        Returns:
            True if successful
        """
        try:
            # Get profiles
            if profile_uuids:
                profiles = []
                for uuid in profile_uuids:
                    try:
                        profile = await self.api.get_profile(uuid, use_cache=False)
                        profiles.append(profile)
                    except Exception as e:
                        logger.warning(f"Failed to get profile {uuid}: {e}")
            else:
                profiles = await self.profiles.get_all_profiles()

            # Convert to dictionaries
            data = {
                "version": "1.0",
                "profiles": [p.to_dict() for p in profiles],
                "total": len(profiles),
            }

            # Save to file
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported {len(profiles)} profiles to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")
            return False

    async def import_from_json(
        self, file_path: Path, skip_existing: bool = True
    ) -> BulkOperationResult:
        """Import profiles from JSON file.

        Args:
            file_path: Input file path
            skip_existing: Skip profiles with existing titles

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        try:
            # Load file
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            profiles_data = data.get("profiles", [])

            # Get existing profiles if checking
            existing_titles = set()
            if skip_existing:
                existing_profiles = await self.profiles.get_all_profiles()
                existing_titles = {p.title for p in existing_profiles}

            # Import profiles
            for profile_data in profiles_data:
                try:
                    title = profile_data.get("title", "")

                    # Skip if exists
                    if skip_existing and title in existing_titles:
                        logger.debug(f"Skipping existing profile: {title}")
                        continue

                    # Create request
                    request = ProfileCreateRequest(
                        title=title,
                        description=profile_data.get("description", ""),
                        tags=profile_data.get("tags", []),
                        browser_type=BrowserType(
                            profile_data.get("browser_type", "chrome")
                        ),
                        start_url=profile_data.get("start_url", "about:blank"),
                    )

                    # Add proxy if present
                    if "proxy" in profile_data and profile_data["proxy"]:
                        request.proxy = Proxy.from_dict(profile_data["proxy"])

                    # Add fingerprint if present
                    if "fingerprint" in profile_data and profile_data["fingerprint"]:
                        request.fingerprint = Fingerprint.from_dict(
                            profile_data["fingerprint"]
                        )

                    # Create profile
                    await self.api.create_profile(request)
                    result.add_success()

                    logger.debug(f"Imported profile: {title}")

                except Exception as e:
                    error_msg = str(e)
                    result.add_failure(profile_data.get("uuid", "unknown"), error_msg)
                    logger.error(f"Failed to import profile: {error_msg}")

            logger.info(
                f"Import from JSON: {result.successful}/{result.total} successful"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to import from JSON: {e}")
            return result

    async def export_to_csv(
        self, file_path: Path, profile_uuids: Optional[List[str]] = None
    ) -> bool:
        """Export profiles to CSV file.

        Args:
            file_path: Output file path
            profile_uuids: List of profile UUIDs (None = all profiles)

        Returns:
            True if successful
        """
        try:
            # Get profiles
            if profile_uuids:
                profiles = []
                for uuid in profile_uuids:
                    try:
                        profile = await self.api.get_profile(uuid, use_cache=False)
                        profiles.append(profile)
                    except Exception as e:
                        logger.warning(f"Failed to get profile {uuid}: {e}")
            else:
                profiles = await self.profiles.get_all_profiles()

            # Prepare CSV rows
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8", newline="") as f:
                fieldnames = [
                    "uuid",
                    "title",
                    "description",
                    "browser_type",
                    "start_url",
                    "tags",
                    "proxy_type",
                    "proxy_host",
                    "proxy_port",
                    "proxy_login",
                    "proxy_password",
                    "notes",
                ]

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for profile in profiles:
                    row = {
                        "uuid": profile.uuid,
                        "title": profile.title,
                        "description": profile.description,
                        "browser_type": profile.browser_type.value,
                        "start_url": profile.start_url,
                        "tags": ",".join(profile.tags),
                        "notes": profile.notes,
                    }

                    # Add proxy info
                    if profile.proxy:
                        row["proxy_type"] = profile.proxy.type.value
                        row["proxy_host"] = profile.proxy.host
                        row["proxy_port"] = profile.proxy.port
                        row["proxy_login"] = profile.proxy.login or ""
                        row["proxy_password"] = profile.proxy.password or ""

                    writer.writerow(row)

            logger.info(f"Exported {len(profiles)} profiles to CSV: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return False

    async def import_from_csv(
        self, file_path: Path, skip_existing: bool = True
    ) -> BulkOperationResult:
        """Import profiles from CSV file.

        Args:
            file_path: Input file path
            skip_existing: Skip profiles with existing titles

        Returns:
            Bulk operation result
        """
        result = BulkOperationResult(total=0, successful=0, failed=0)

        try:
            # Get existing profiles if checking
            existing_titles = set()
            if skip_existing:
                existing_profiles = await self.profiles.get_all_profiles()
                existing_titles = {p.title for p in existing_profiles}

            # Load CSV
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    try:
                        title = row.get("title", "")

                        # Skip if exists
                        if skip_existing and title in existing_titles:
                            logger.debug(f"Skipping existing profile: {title}")
                            continue

                        # Create request
                        request = ProfileCreateRequest(
                            title=title,
                            description=row.get("description", ""),
                            tags=row.get("tags", "").split(",") if row.get("tags") else [],
                            browser_type=BrowserType(row.get("browser_type", "chrome")),
                            start_url=row.get("start_url", "about:blank"),
                        )

                        # Add proxy if present
                        if row.get("proxy_host") and row.get("proxy_port"):
                            from src.octo.models import ProxyType

                            request.proxy = Proxy(
                                type=ProxyType(row.get("proxy_type", "http")),
                                host=row["proxy_host"],
                                port=int(row["proxy_port"]),
                                login=row.get("proxy_login") or None,
                                password=row.get("proxy_password") or None,
                            )

                        # Create profile
                        await self.api.create_profile(request)
                        result.add_success()

                        logger.debug(f"Imported profile: {title}")

                    except Exception as e:
                        error_msg = str(e)
                        result.add_failure(row.get("uuid", "unknown"), error_msg)
                        logger.error(f"Failed to import profile: {error_msg}")

            logger.info(
                f"Import from CSV: {result.successful}/{result.total} successful"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to import from CSV: {e}")
            return result

    async def export_proxies_to_file(
        self, file_path: Path, profile_uuids: Optional[List[str]] = None
    ) -> bool:
        """Export proxies from profiles to text file.

        Args:
            file_path: Output file path
            profile_uuids: List of profile UUIDs (None = all profiles)

        Returns:
            True if successful
        """
        try:
            # Get profiles
            if profile_uuids:
                profiles = []
                for uuid in profile_uuids:
                    try:
                        profile = await self.api.get_profile(uuid, use_cache=False)
                        profiles.append(profile)
                    except Exception as e:
                        logger.warning(f"Failed to get profile {uuid}: {e}")
            else:
                profiles = await self.profiles.get_all_profiles()

            # Extract proxies
            proxies = []
            for profile in profiles:
                if profile.proxy:
                    proxies.append(str(profile.proxy))

            # Save to file
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                for proxy in proxies:
                    f.write(f"{proxy}\n")

            logger.info(f"Exported {len(proxies)} proxies to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export proxies: {e}")
            return False

    async def backup_all_profiles(self, backup_dir: Path) -> bool:
        """Create full backup of all profiles.

        Args:
            backup_dir: Backup directory

        Returns:
            True if successful
        """
        try:
            from datetime import datetime

            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"profiles_backup_{timestamp}.json"

            # Export all profiles
            success = await self.export_to_json(backup_file)

            if success:
                logger.info(f"Created backup: {backup_file}")

            return success

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

    async def restore_from_backup(
        self, backup_file: Path, skip_existing: bool = True
    ) -> BulkOperationResult:
        """Restore profiles from backup.

        Args:
            backup_file: Backup file path
            skip_existing: Skip profiles with existing titles

        Returns:
            Bulk operation result
        """
        logger.info(f"Restoring from backup: {backup_file}")
        return await self.import_from_json(backup_file, skip_existing)

    async def export_profile_summary(
        self, file_path: Path, profile_uuids: Optional[List[str]] = None
    ) -> bool:
        """Export profile summary (without sensitive data).

        Args:
            file_path: Output file path
            profile_uuids: List of profile UUIDs (None = all profiles)

        Returns:
            True if successful
        """
        try:
            # Get profiles
            if profile_uuids:
                profiles = []
                for uuid in profile_uuids:
                    try:
                        profile = await self.api.get_profile(uuid, use_cache=False)
                        profiles.append(profile)
                    except Exception as e:
                        logger.warning(f"Failed to get profile {uuid}: {e}")
            else:
                profiles = await self.profiles.get_all_profiles()

            # Create summary
            summary = []
            for profile in profiles:
                summary.append(
                    {
                        "uuid": profile.uuid,
                        "title": profile.title,
                        "description": profile.description,
                        "browser_type": profile.browser_type.value,
                        "tags": profile.tags,
                        "has_proxy": profile.proxy is not None,
                        "proxy_type": profile.proxy.type.value if profile.proxy else None,
                        "notes": profile.notes,
                    }
                )

            # Save to file
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"profiles": summary, "total": len(summary)},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            logger.info(f"Exported summary for {len(profiles)} profiles to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export summary: {e}")
            return False

    async def get_export_statistics(
        self, profile_uuids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get statistics for profiles to be exported.

        Args:
            profile_uuids: List of profile UUIDs (None = all profiles)

        Returns:
            Statistics dictionary
        """
        # Get profiles
        if profile_uuids:
            profiles = []
            for uuid in profile_uuids:
                try:
                    profile = await self.api.get_profile(uuid, use_cache=False)
                    profiles.append(profile)
                except Exception as e:
                    logger.warning(f"Failed to get profile {uuid}: {e}")
        else:
            profiles = await self.profiles.get_all_profiles()

        # Calculate statistics
        with_proxy = sum(1 for p in profiles if p.proxy is not None)
        with_tags = sum(1 for p in profiles if p.tags)

        browser_counts: Dict[str, int] = {}
        for profile in profiles:
            browser = profile.browser_type.name
            browser_counts[browser] = browser_counts.get(browser, 0) + 1

        return {
            "total_profiles": len(profiles),
            "with_proxy": with_proxy,
            "without_proxy": len(profiles) - with_proxy,
            "with_tags": with_tags,
            "by_browser": browser_counts,
        }
