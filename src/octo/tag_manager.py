"""
Tag management module for Octo Browser.

Provides tag operations and organization.
"""

from typing import List, Optional, Dict, Any
from loguru import logger

from src.octo.api import OctoAPI
from src.octo.models import Tag


class TagManager:
    """Tag management and operations."""

    def __init__(self, api: OctoAPI):
        """Initialize tag manager.

        Args:
            api: OctoAPI instance
        """
        self.api = api
        self._tags_cache: Optional[List[Tag]] = None
        logger.info("TagManager initialized")

    async def get_all_tags(self, use_cache: bool = True) -> List[Tag]:
        """Get all tags.

        Args:
            use_cache: Whether to use local cache

        Returns:
            List of tags
        """
        if use_cache and self._tags_cache is not None:
            return self._tags_cache

        tags = await self.api.get_tags(use_cache=use_cache)
        self._tags_cache = tags

        logger.info(f"Retrieved {len(tags)} tags")
        return tags

    async def get_tag_by_uuid(self, tag_uuid: str) -> Optional[Tag]:
        """Get tag by UUID.

        Args:
            tag_uuid: Tag UUID

        Returns:
            Tag or None
        """
        tags = await self.get_all_tags()

        for tag in tags:
            if tag.uuid == tag_uuid:
                return tag

        return None

    async def get_tag_by_name(self, name: str, exact_match: bool = True) -> Optional[Tag]:
        """Get tag by name.

        Args:
            name: Tag name
            exact_match: Exact match or contains

        Returns:
            First matching tag or None
        """
        tags = await self.get_all_tags()

        name_lower = name.lower()

        for tag in tags:
            tag_name_lower = tag.name.lower()

            if exact_match:
                if tag_name_lower == name_lower:
                    return tag
            else:
                if name_lower in tag_name_lower:
                    return tag

        return None

    async def search_tags(self, query: str) -> List[Tag]:
        """Search tags by name.

        Args:
            query: Search query

        Returns:
            Matching tags
        """
        tags = await self.get_all_tags()
        query_lower = query.lower()

        results = [tag for tag in tags if query_lower in tag.name.lower()]

        logger.info(f"Found {len(results)} tags matching '{query}'")
        return results

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
        # Check if tag already exists
        existing = await self.get_tag_by_name(name, exact_match=True)
        if existing:
            logger.warning(f"Tag '{name}' already exists")
            return existing

        tag = await self.api.create_tag(name, color)

        # Invalidate cache
        self._tags_cache = None

        logger.info(f"Created tag: {name} ({tag.uuid})")
        return tag

    async def update_tag(
        self, tag_uuid: str, name: Optional[str] = None, color: Optional[str] = None
    ) -> Tag:
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
        tag = await self.api.update_tag(tag_uuid, name, color)

        # Invalidate cache
        self._tags_cache = None

        logger.info(f"Updated tag: {tag_uuid}")
        return tag

    async def delete_tag(self, tag_uuid: str) -> bool:
        """Delete tag.

        Args:
            tag_uuid: Tag UUID

        Returns:
            True if successful

        Raises:
            Exception: If deletion fails
        """
        result = await self.api.delete_tag(tag_uuid)

        # Invalidate cache
        self._tags_cache = None

        logger.info(f"Deleted tag: {tag_uuid}")
        return result

    async def get_or_create_tag(self, name: str, color: str = "#808080") -> Tag:
        """Get existing tag or create new one.

        Args:
            name: Tag name
            color: Tag color (used only if creating)

        Returns:
            Tag instance
        """
        # Try to find existing
        existing = await self.get_tag_by_name(name, exact_match=True)
        if existing:
            return existing

        # Create new
        return await self.create_tag(name, color)

    async def bulk_create_tags(self, names: List[str], color: str = "#808080") -> List[Tag]:
        """Create multiple tags.

        Args:
            names: List of tag names
            color: Tag color (same for all)

        Returns:
            List of created/existing tags
        """
        tags: List[Tag] = []

        for name in names:
            try:
                tag = await self.get_or_create_tag(name, color)
                tags.append(tag)
                logger.debug(f"Tag ready: {name}")
            except Exception as e:
                logger.error(f"Failed to create tag '{name}': {e}")

        logger.info(f"Bulk create tags: {len(tags)}/{len(names)} successful")
        return tags

    async def rename_tag(self, tag_uuid: str, new_name: str) -> Tag:
        """Rename tag.

        Args:
            tag_uuid: Tag UUID
            new_name: New name

        Returns:
            Updated tag
        """
        return await self.update_tag(tag_uuid, name=new_name)

    async def change_color(self, tag_uuid: str, new_color: str) -> Tag:
        """Change tag color.

        Args:
            tag_uuid: Tag UUID
            new_color: New color (hex)

        Returns:
            Updated tag
        """
        return await self.update_tag(tag_uuid, color=new_color)

    async def find_or_create_by_pattern(self, prefix: str, count: int, color: str = "#808080") -> List[Tag]:
        """Find or create tags by pattern.

        Args:
            prefix: Tag name prefix
            count: Number of tags
            color: Tag color for new tags

        Returns:
            List of tags
        """
        tags: List[Tag] = []

        for i in range(1, count + 1):
            name = f"{prefix}{i}"
            tag = await self.get_or_create_tag(name, color)
            tags.append(tag)

        logger.info(f"Pattern tags ready: {len(tags)} tags with prefix '{prefix}'")
        return tags

    def clear_cache(self) -> None:
        """Clear local tag cache."""
        self._tags_cache = None
        logger.debug("Tag cache cleared")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get tag statistics.

        Returns:
            Statistics dictionary
        """
        tags = await self.get_all_tags()

        # Count by color
        color_counts: Dict[str, int] = {}
        for tag in tags:
            color = tag.color
            color_counts[color] = color_counts.get(color, 0) + 1

        # Most common colors
        top_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_tags": len(tags),
            "unique_colors": len(color_counts),
            "color_distribution": color_counts,
            "top_colors": top_colors,
        }

    async def export_tags(self) -> List[Dict[str, str]]:
        """Export all tags.

        Returns:
            List of tag dictionaries
        """
        tags = await self.get_all_tags()
        return [tag.to_dict() for tag in tags]

    async def import_tags(self, tags_data: List[Dict[str, str]]) -> Dict[str, int]:
        """Import tags from data.

        Args:
            tags_data: List of tag dictionaries (name, color)

        Returns:
            Statistics: created, existing counts
        """
        created = 0
        existing = 0

        for data in tags_data:
            try:
                name = data.get("name")
                color = data.get("color", "#808080")

                if not name:
                    continue

                # Check if exists
                existing_tag = await self.get_tag_by_name(name, exact_match=True)

                if existing_tag:
                    existing += 1
                else:
                    await self.create_tag(name, color)
                    created += 1

            except Exception as e:
                logger.error(f"Failed to import tag: {e}")

        logger.info(f"Import tags: {created} created, {existing} existing")
        return {"created": created, "existing": existing, "total": len(tags_data)}

    async def organize_by_color_scheme(self) -> Dict[str, List[Tag]]:
        """Organize tags by color.

        Returns:
            Dictionary mapping colors to tags
        """
        tags = await self.get_all_tags()

        organized: Dict[str, List[Tag]] = {}

        for tag in tags:
            color = tag.color
            if color not in organized:
                organized[color] = []
            organized[color].append(tag)

        return organized

    async def suggest_similar_tags(self, name: str, max_suggestions: int = 5) -> List[Tag]:
        """Suggest similar tag names.

        Args:
            name: Tag name to find similar tags for
            max_suggestions: Maximum number of suggestions

        Returns:
            List of similar tags
        """
        tags = await self.get_all_tags()
        name_lower = name.lower()

        # Simple similarity: tags that contain or are contained in the query
        similar: List[Tag] = []

        for tag in tags:
            tag_name_lower = tag.name.lower()

            # Exact match
            if tag_name_lower == name_lower:
                continue

            # Contains or contained
            if name_lower in tag_name_lower or tag_name_lower in name_lower:
                similar.append(tag)

        return similar[:max_suggestions]
