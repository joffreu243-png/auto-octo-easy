"""
Template manager for OctoMaster Pro.

Manages workflow templates including loading, searching, and creation.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
import json
import uuid
from loguru import logger


@dataclass
class Template:
    """Workflow template."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: str = ""  # scraping, testing, smm, ecommerce
    tags: List[str] = field(default_factory=list)
    difficulty: str = "easy"  # easy, medium, hard
    author: str = "OctoMaster Team"
    version: str = "1.0"
    icon: Optional[str] = None

    # Template inputs (configurable by user)
    inputs: List[Dict[str, Any]] = field(default_factory=list)

    # Template outputs
    outputs: List[Dict[str, Any]] = field(default_factory=list)

    # Workflow data
    workflow: Optional[Dict[str, Any]] = None

    # Requirements
    requires_browser: bool = True
    requires_api_key: bool = False
    estimated_duration: Optional[int] = None  # seconds

    def save(self, path: Path) -> None:
        """Save template to file.

        Args:
            path: Path to save template
        """
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "difficulty": self.difficulty,
            "author": self.author,
            "version": self.version,
            "icon": self.icon,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "workflow": self.workflow,
            "requires_browser": self.requires_browser,
            "requires_api_key": self.requires_api_key,
            "estimated_duration": self.estimated_duration,
        }

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.debug(f"Saved template: {self.name} to {path}")

    @classmethod
    def load(cls, path: Path) -> "Template":
        """Load template from file.

        Args:
            path: Path to template file

        Returns:
            Template instance
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.debug(f"Loaded template from {path}")
        return cls(**data)

    def apply_inputs(self, input_values: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user input values to workflow.

        Args:
            input_values: User-provided input values

        Returns:
            Workflow with applied values
        """
        if not self.workflow:
            return {}

        workflow = json.loads(json.dumps(self.workflow))  # Deep copy

        # Replace placeholders in workflow
        workflow_str = json.dumps(workflow)

        for input_def in self.inputs:
            input_name = input_def["name"]
            if input_name in input_values:
                placeholder = "{" + input_name + "}"
                value = str(input_values[input_name])
                workflow_str = workflow_str.replace(placeholder, value)

        return json.loads(workflow_str)

    def validate_inputs(self, input_values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user input values.

        Args:
            input_values: User-provided input values

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        for input_def in self.inputs:
            input_name = input_def["name"]
            input_type = input_def.get("type", "string")
            required = input_def.get("required", True)

            # Check if required input is provided
            if required and input_name not in input_values:
                errors.append(f"Required input '{input_name}' is missing")
                continue

            if input_name in input_values:
                value = input_values[input_name]

                # Type validation
                if input_type == "integer" and not isinstance(value, int):
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        errors.append(f"Input '{input_name}' must be an integer")

                elif input_type == "number" and not isinstance(value, (int, float)):
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        errors.append(f"Input '{input_name}' must be a number")

                elif input_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Input '{input_name}' must be a boolean")

                # Range validation
                if "min" in input_def and value < input_def["min"]:
                    errors.append(
                        f"Input '{input_name}' must be >= {input_def['min']}"
                    )

                if "max" in input_def and value > input_def["max"]:
                    errors.append(
                        f"Input '{input_name}' must be <= {input_def['max']}"
                    )

        return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}


class TemplateManager:
    """Manage workflow templates."""

    def __init__(self, templates_dir: Path):
        """Initialize template manager.

        Args:
            templates_dir: Directory containing templates
        """
        self.templates_dir = templates_dir
        self.templates: Dict[str, Template] = {}

        logger.info(f"TemplateManager initialized: {templates_dir}")

    def load_all_templates(self) -> int:
        """Load all templates from directory.

        Returns:
            Number of templates loaded
        """
        self.templates.clear()
        count = 0

        # Load builtin templates
        builtin_dir = self.templates_dir / "builtin"
        if builtin_dir.exists():
            count += self._load_from_directory(builtin_dir)

        # Load user templates
        user_dir = self.templates_dir / "user"
        if user_dir.exists():
            count += self._load_from_directory(user_dir)

        logger.info(f"Loaded {count} templates")
        return count

    def _load_from_directory(self, directory: Path) -> int:
        """Load templates from directory recursively.

        Args:
            directory: Directory to load from

        Returns:
            Number of templates loaded
        """
        count = 0

        for template_file in directory.rglob("*.json"):
            try:
                template = Template.load(template_file)
                self.templates[template.id] = template
                count += 1
                logger.debug(f"Loaded template: {template.name}")
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")

        return count

    def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID.

        Args:
            template_id: Template ID

        Returns:
            Template or None
        """
        return self.templates.get(template_id)

    def get_all_templates(self) -> List[Template]:
        """Get all templates.

        Returns:
            List of all templates
        """
        return list(self.templates.values())

    def get_by_category(self, category: str) -> List[Template]:
        """Get templates by category.

        Args:
            category: Category name

        Returns:
            Templates in category
        """
        return [t for t in self.templates.values() if t.category == category]

    def get_by_difficulty(self, difficulty: str) -> List[Template]:
        """Get templates by difficulty.

        Args:
            difficulty: Difficulty level (easy, medium, hard)

        Returns:
            Templates with difficulty
        """
        return [t for t in self.templates.values() if t.difficulty == difficulty]

    def search(self, query: str) -> List[Template]:
        """Search templates by name, description, or tags.

        Args:
            query: Search query

        Returns:
            Matching templates
        """
        query_lower = query.lower()
        results = []

        for template in self.templates.values():
            if (
                query_lower in template.name.lower()
                or query_lower in template.description.lower()
                or any(query_lower in tag.lower() for tag in template.tags)
            ):
                results.append(template)

        logger.debug(f"Search '{query}' found {len(results)} templates")
        return results

    def create_from_workflow(
        self,
        workflow: Dict[str, Any],
        name: str,
        description: str,
        category: str,
        tags: List[str],
        difficulty: str = "medium",
    ) -> Template:
        """Create template from existing workflow.

        Args:
            workflow: Workflow data
            name: Template name
            description: Template description
            category: Category
            tags: Tags
            difficulty: Difficulty level

        Returns:
            Created template
        """
        template = Template(
            name=name,
            description=description,
            category=category,
            tags=tags,
            difficulty=difficulty,
            workflow=workflow,
        )

        self.templates[template.id] = template

        logger.info(f"Created template: {name}")
        return template

    def export_template(self, template_id: str, path: Path) -> bool:
        """Export template to file.

        Args:
            template_id: Template ID
            path: Export path

        Returns:
            True if successful
        """
        template = self.templates.get(template_id)

        if not template:
            logger.error(f"Template not found: {template_id}")
            return False

        try:
            template.save(path)
            logger.info(f"Exported template to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export template: {e}")
            return False

    def import_template(self, path: Path) -> Optional[Template]:
        """Import template from file.

        Args:
            path: Template file path

        Returns:
            Imported template or None
        """
        try:
            template = Template.load(path)
            self.templates[template.id] = template

            logger.info(f"Imported template: {template.name}")
            return template
        except Exception as e:
            logger.error(f"Failed to import template: {e}")
            return None

    def delete_template(self, template_id: str) -> bool:
        """Delete template.

        Args:
            template_id: Template ID

        Returns:
            True if successful
        """
        if template_id in self.templates:
            del self.templates[template_id]
            logger.info(f"Deleted template: {template_id}")
            return True

        return False

    def get_categories(self) -> List[str]:
        """Get all unique categories.

        Returns:
            List of categories
        """
        categories = set()
        for template in self.templates.values():
            if template.category:
                categories.add(template.category)

        return sorted(categories)

    def get_tags(self) -> List[str]:
        """Get all unique tags.

        Returns:
            List of tags
        """
        tags = set()
        for template in self.templates.values():
            tags.update(template.tags)

        return sorted(tags)

    def get_statistics(self) -> Dict[str, Any]:
        """Get template statistics.

        Returns:
            Statistics dictionary
        """
        total = len(self.templates)

        by_category = {}
        by_difficulty = {}

        for template in self.templates.values():
            # Count by category
            cat = template.category or "uncategorized"
            by_category[cat] = by_category.get(cat, 0) + 1

            # Count by difficulty
            diff = template.difficulty
            by_difficulty[diff] = by_difficulty.get(diff, 0) + 1

        return {
            "total": total,
            "by_category": by_category,
            "by_difficulty": by_difficulty,
            "categories": self.get_categories(),
            "tags": self.get_tags(),
        }
