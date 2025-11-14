"""
Template marketplace for OctoMaster Pro.

Allows sharing and downloading templates from community.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import httpx
from loguru import logger

from src.templates.manager import Template


class TemplateMarketplace:
    """Template marketplace client."""

    def __init__(
        self,
        marketplace_url: str = "https://templates.octomaster.pro/api",
        cache_dir: Optional[Path] = None,
    ):
        """Initialize marketplace client.

        Args:
            marketplace_url: Marketplace API URL
            cache_dir: Local cache directory
        """
        self.marketplace_url = marketplace_url.rstrip("/")
        self.cache_dir = cache_dir or Path.home() / ".octomaster" / "template_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.client = httpx.AsyncClient(timeout=30.0)

        logger.info("TemplateMarketplace initialized")

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    async def search_templates(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search templates in marketplace.

        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            limit: Maximum results

        Returns:
            List of template metadata
        """
        try:
            params = {"limit": limit}

            if query:
                params["q"] = query

            if category:
                params["category"] = category

            if tags:
                params["tags"] = ",".join(tags)

            response = await self.client.get(
                f"{self.marketplace_url}/templates/search", params=params
            )

            response.raise_for_status()
            data = response.json()

            templates = data.get("templates", [])
            logger.info(f"Found {len(templates)} templates in marketplace")

            return templates

        except Exception as e:
            logger.error(f"Failed to search marketplace: {e}")
            return []

    async def get_template_details(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed template information.

        Args:
            template_id: Template ID

        Returns:
            Template metadata
        """
        try:
            response = await self.client.get(
                f"{self.marketplace_url}/templates/{template_id}"
            )

            response.raise_for_status()
            data = response.json()

            logger.debug(f"Got template details: {template_id}")
            return data

        except Exception as e:
            logger.error(f"Failed to get template details: {e}")
            return None

    async def download_template(
        self, template_id: str, save_path: Optional[Path] = None
    ) -> Optional[Template]:
        """Download template from marketplace.

        Args:
            template_id: Template ID
            save_path: Path to save template (optional)

        Returns:
            Downloaded template
        """
        try:
            # Get template data
            response = await self.client.get(
                f"{self.marketplace_url}/templates/{template_id}/download"
            )

            response.raise_for_status()
            template_data = response.json()

            # Create template
            template = Template(**template_data)

            # Save to cache
            cache_path = self.cache_dir / f"{template_id}.json"
            template.save(cache_path)

            # Save to custom path if provided
            if save_path:
                template.save(save_path)

            logger.info(f"Downloaded template: {template.name}")
            return template

        except Exception as e:
            logger.error(f"Failed to download template: {e}")
            return None

    async def upload_template(
        self, template: Template, api_key: str
    ) -> Optional[str]:
        """Upload template to marketplace.

        Args:
            template: Template to upload
            api_key: API key for authentication

        Returns:
            Template ID if successful
        """
        try:
            headers = {"Authorization": f"Bearer {api_key}"}

            # Convert template to dict
            template_data = {
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "tags": template.tags,
                "difficulty": template.difficulty,
                "author": template.author,
                "version": template.version,
                "inputs": template.inputs,
                "outputs": template.outputs,
                "workflow": template.workflow,
            }

            response = await self.client.post(
                f"{self.marketplace_url}/templates/upload",
                json=template_data,
                headers=headers,
            )

            response.raise_for_status()
            data = response.json()

            template_id = data.get("template_id")
            logger.info(f"Uploaded template: {template.name} (ID: {template_id})")

            return template_id

        except Exception as e:
            logger.error(f"Failed to upload template: {e}")
            return None

    async def get_featured_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get featured templates.

        Args:
            limit: Maximum results

        Returns:
            List of featured templates
        """
        try:
            response = await self.client.get(
                f"{self.marketplace_url}/templates/featured", params={"limit": limit}
            )

            response.raise_for_status()
            data = response.json()

            templates = data.get("templates", [])
            logger.info(f"Got {len(templates)} featured templates")

            return templates

        except Exception as e:
            logger.error(f"Failed to get featured templates: {e}")
            return []

    async def get_popular_templates(
        self, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get popular templates.

        Args:
            category: Filter by category
            limit: Maximum results

        Returns:
            List of popular templates
        """
        try:
            params = {"limit": limit}
            if category:
                params["category"] = category

            response = await self.client.get(
                f"{self.marketplace_url}/templates/popular", params=params
            )

            response.raise_for_status()
            data = response.json()

            templates = data.get("templates", [])
            logger.info(f"Got {len(templates)} popular templates")

            return templates

        except Exception as e:
            logger.error(f"Failed to get popular templates: {e}")
            return []

    async def rate_template(
        self, template_id: str, rating: int, api_key: str
    ) -> bool:
        """Rate a template.

        Args:
            template_id: Template ID
            rating: Rating (1-5)
            api_key: API key

        Returns:
            True if successful
        """
        try:
            headers = {"Authorization": f"Bearer {api_key}"}

            response = await self.client.post(
                f"{self.marketplace_url}/templates/{template_id}/rate",
                json={"rating": rating},
                headers=headers,
            )

            response.raise_for_status()
            logger.info(f"Rated template {template_id}: {rating} stars")

            return True

        except Exception as e:
            logger.error(f"Failed to rate template: {e}")
            return False

    async def report_template(
        self, template_id: str, reason: str, api_key: str
    ) -> bool:
        """Report a template.

        Args:
            template_id: Template ID
            reason: Report reason
            api_key: API key

        Returns:
            True if successful
        """
        try:
            headers = {"Authorization": f"Bearer {api_key}"}

            response = await self.client.post(
                f"{self.marketplace_url}/templates/{template_id}/report",
                json={"reason": reason},
                headers=headers,
            )

            response.raise_for_status()
            logger.info(f"Reported template: {template_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to report template: {e}")
            return False

    def get_cached_templates(self) -> List[Path]:
        """Get list of cached templates.

        Returns:
            List of cached template files
        """
        if not self.cache_dir.exists():
            return []

        return list(self.cache_dir.glob("*.json"))

    def clear_cache(self) -> int:
        """Clear template cache.

        Returns:
            Number of files deleted
        """
        count = 0

        for template_file in self.get_cached_templates():
            try:
                template_file.unlink()
                count += 1
            except Exception as e:
                logger.error(f"Failed to delete cache file {template_file}: {e}")

        logger.info(f"Cleared {count} cached templates")
        return count
