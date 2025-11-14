"""
Template Manager for organizing and accessing workflow templates.
"""

from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger

from octomaster.core.templates.template import Template


class TemplateManager:
    """
    Manages a library of workflow templates.

    Features:
    - Load templates from directory
    - Search and filter templates
    - Categorize templates
    - Template marketplace integration (future)
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize template manager.

        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = templates_dir or Path("resources/templates")
        self.templates: List[Template] = []
        self.templates_by_id: Dict[str, Template] = {}
        self.templates_by_category: Dict[str, List[Template]] = {}

        # Ensure directory exists
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Load templates
        self.load_all()

    def load_all(self):
        """Load all templates from directory."""
        self.templates = []
        self.templates_by_id = {}
        self.templates_by_category = {}

        # Find all .template files
        template_files = list(self.templates_dir.glob("**/*.template"))

        logger.info(f"Found {len(template_files)} template files")

        for file_path in template_files:
            try:
                template = Template.load(file_path)
                self.add_template(template)
            except Exception as e:
                logger.error(f"Failed to load template {file_path}: {e}")

        logger.info(f"Loaded {len(self.templates)} templates")

    def add_template(self, template: Template):
        """Add template to the library."""
        self.templates.append(template)
        self.templates_by_id[template.id] = template

        # Add to category
        category = template.category
        if category not in self.templates_by_category:
            self.templates_by_category[category] = []
        self.templates_by_category[category].append(template)

    def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID."""
        return self.templates_by_id.get(template_id)

    def get_by_category(self, category: str) -> List[Template]:
        """Get all templates in a category."""
        return self.templates_by_category.get(category, [])

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
    ) -> List[Template]:
        """
        Search templates.

        Args:
            query: Search query (searches name and description)
            category: Filter by category
            tags: Filter by tags (template must have all tags)
            difficulty: Filter by difficulty

        Returns:
            List of matching templates
        """
        results = self.templates.copy()

        # Filter by category
        if category:
            results = [t for t in results if t.category == category]

        # Filter by difficulty
        if difficulty:
            results = [t for t in results if t.difficulty == difficulty]

        # Filter by tags
        if tags:
            results = [
                t for t in results if all(tag in t.tags for tag in tags)
            ]

        # Search query
        if query:
            query_lower = query.lower()
            results = [
                t
                for t in results
                if query_lower in t.name.lower()
                or query_lower in t.description.lower()
            ]

        return results

    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return list(self.templates_by_category.keys())

    def get_featured(self, limit: int = 10) -> List[Template]:
        """Get featured templates (by rating and downloads)."""
        sorted_templates = sorted(
            self.templates,
            key=lambda t: (t.rating, t.downloads),
            reverse=True,
        )
        return sorted_templates[:limit]

    def get_popular(self, limit: int = 10) -> List[Template]:
        """Get most popular templates (by downloads)."""
        sorted_templates = sorted(
            self.templates, key=lambda t: t.downloads, reverse=True
        )
        return sorted_templates[:limit]

    def get_recent(self, limit: int = 10) -> List[Template]:
        """Get most recent templates."""
        # For now, just return first N templates
        # In production, would sort by creation date
        return self.templates[:limit]

    def export_template(self, template: Template, destination: Path):
        """Export template to file."""
        template.save(destination)
        logger.info(f"Exported template {template.name} to {destination}")

    def import_template(self, source: Path) -> Template:
        """Import template from file."""
        template = Template.load(source)
        self.add_template(template)

        logger.info(f"Imported template: {template.name}")
        return template

    def delete_template(self, template_id: str) -> bool:
        """Delete template from library."""
        template = self.get_template(template_id)
        if not template:
            return False

        # Remove from all data structures
        self.templates = [t for t in self.templates if t.id != template_id]
        if template_id in self.templates_by_id:
            del self.templates_by_id[template_id]

        # Remove from category
        category = template.category
        if category in self.templates_by_category:
            self.templates_by_category[category] = [
                t for t in self.templates_by_category[category] if t.id != template_id
            ]

        logger.info(f"Deleted template: {template.name}")
        return True

    def create_template_from_workflow(
        self, workflow, name: str, description: str, category: str, **kwargs
    ) -> Template:
        """Create a template from an existing workflow."""
        from uuid import uuid4

        template = Template(
            id=str(uuid4()),
            name=name,
            description=description,
            category=category,
            workflow=workflow,
            **kwargs,
        )

        self.add_template(template)

        logger.info(f"Created template: {name}")
        return template

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the template library."""
        return {
            "total_templates": len(self.templates),
            "categories": len(self.templates_by_category),
            "total_downloads": sum(t.downloads for t in self.templates),
            "average_rating": (
                sum(t.rating for t in self.templates) / len(self.templates)
                if self.templates
                else 0
            ),
        }

    def __repr__(self) -> str:
        return f"TemplateManager(templates={len(self.templates)}, categories={len(self.templates_by_category)})"
