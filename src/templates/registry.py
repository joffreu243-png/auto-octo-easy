"""
Template registry for OctoMaster Pro.

Central registry for template types and categories.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class TemplateCategory:
    """Template category definition."""

    id: str
    name: str
    description: str
    icon: str
    color: str


@dataclass
class InputType:
    """Template input type definition."""

    id: str
    name: str
    python_type: type
    default_value: Any = None


class TemplateRegistry:
    """Central registry for templates."""

    # Predefined categories
    CATEGORIES = {
        "scraping": TemplateCategory(
            id="scraping",
            name="Web Scraping",
            description="Extract data from websites",
            icon="🕷️",
            color="#4CAF50",
        ),
        "testing": TemplateCategory(
            id="testing",
            name="Automated Testing",
            description="Test web applications",
            icon="🧪",
            color="#2196F3",
        ),
        "smm": TemplateCategory(
            id="smm",
            name="Social Media Marketing",
            description="Automate social media tasks",
            icon="📱",
            color="#E91E63",
        ),
        "ecommerce": TemplateCategory(
            id="ecommerce",
            name="E-Commerce",
            description="Online shopping automation",
            icon="🛒",
            color="#FF9800",
        ),
        "monitoring": TemplateCategory(
            id="monitoring",
            name="Monitoring",
            description="Monitor websites and services",
            icon="📊",
            color="#9C27B0",
        ),
        "data_entry": TemplateCategory(
            id="data_entry",
            name="Data Entry",
            description="Automated form filling",
            icon="⌨️",
            color="#607D8B",
        ),
        "seo": TemplateCategory(
            id="seo",
            name="SEO Tools",
            description="Search engine optimization",
            icon="🔍",
            color="#00BCD4",
        ),
        "research": TemplateCategory(
            id="research",
            name="Research",
            description="Data collection and research",
            icon="🔬",
            color="#3F51B5",
        ),
    }

    # Input types
    INPUT_TYPES = {
        "string": InputType(
            id="string", name="Text", python_type=str, default_value=""
        ),
        "integer": InputType(id="integer", name="Number", python_type=int, default_value=0),
        "number": InputType(id="number", name="Decimal", python_type=float, default_value=0.0),
        "boolean": InputType(
            id="boolean", name="Yes/No", python_type=bool, default_value=False
        ),
        "url": InputType(
            id="url", name="URL", python_type=str, default_value="https://"
        ),
        "email": InputType(
            id="email", name="Email", python_type=str, default_value=""
        ),
        "selector": InputType(
            id="selector", name="CSS Selector", python_type=str, default_value=""
        ),
        "file": InputType(id="file", name="File Path", python_type=str, default_value=""),
        "list": InputType(
            id="list", name="List", python_type=list, default_value=[]
        ),
    }

    @classmethod
    def get_category(cls, category_id: str) -> TemplateCategory:
        """Get category by ID.

        Args:
            category_id: Category ID

        Returns:
            TemplateCategory instance
        """
        return cls.CATEGORIES.get(category_id, cls.CATEGORIES["scraping"])

    @classmethod
    def get_all_categories(cls) -> List[TemplateCategory]:
        """Get all categories.

        Returns:
            List of categories
        """
        return list(cls.CATEGORIES.values())

    @classmethod
    def get_input_type(cls, type_id: str) -> InputType:
        """Get input type by ID.

        Args:
            type_id: Input type ID

        Returns:
            InputType instance
        """
        return cls.INPUT_TYPES.get(type_id, cls.INPUT_TYPES["string"])

    @classmethod
    def get_all_input_types(cls) -> List[InputType]:
        """Get all input types.

        Returns:
            List of input types
        """
        return list(cls.INPUT_TYPES.values())

    @classmethod
    def validate_category(cls, category_id: str) -> bool:
        """Check if category exists.

        Args:
            category_id: Category ID

        Returns:
            True if valid
        """
        return category_id in cls.CATEGORIES

    @classmethod
    def validate_input_type(cls, type_id: str) -> bool:
        """Check if input type exists.

        Args:
            type_id: Input type ID

        Returns:
            True if valid
        """
        return type_id in cls.INPUT_TYPES
