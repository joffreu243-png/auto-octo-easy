"""
Template class for workflow templates.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json

from octomaster.core.workflow import Workflow


@dataclass
class TemplateInput:
    """Input parameter for a template."""

    name: str
    label: str
    type: str  # string, number, boolean, list
    description: str = ""
    default: Any = None
    required: bool = False
    options: Optional[List[str]] = None  # For select/dropdown

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "label": self.label,
            "type": self.type,
            "description": self.description,
            "default": self.default,
            "required": self.required,
            "options": self.options,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateInput":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            label=data["label"],
            type=data["type"],
            description=data.get("description", ""),
            default=data.get("default"),
            required=data.get("required", False),
            options=data.get("options"),
        )


@dataclass
class Template:
    """
    Workflow template.

    Templates allow users to create pre-configured workflows with
    customizable parameters.
    """

    id: str
    name: str
    description: str
    category: str  # scraping, testing, smm, ecommerce, forms, monitoring
    difficulty: str = "easy"  # easy, medium, hard
    author: str = ""
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)

    # Template configuration
    inputs: List[TemplateInput] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)

    # Workflow
    workflow: Optional[Workflow] = None

    # Metadata
    icon: str = "📄"
    preview_image: Optional[str] = None
    documentation_url: Optional[str] = None
    downloads: int = 0
    rating: float = 0.0

    def instantiate(self, parameters: Dict[str, Any]) -> Workflow:
        """
        Create a workflow instance from this template with given parameters.

        Args:
            parameters: Dictionary of parameter values

        Returns:
            Workflow instance with parameters applied
        """
        if not self.workflow:
            raise ValueError("Template has no workflow defined")

        # Clone the workflow
        workflow_data = self.workflow.to_dict()
        workflow = Workflow.from_dict(workflow_data)

        # Apply parameters to blocks
        for block in workflow.blocks:
            for param_name, param_value in block.parameters.items():
                # Replace template variables like {{search_query}}
                if isinstance(param_value, str) and "{{" in param_value:
                    for input_name, input_value in parameters.items():
                        placeholder = f"{{{{{input_name}}}}}"
                        if placeholder in param_value:
                            param_value = param_value.replace(placeholder, str(input_value))
                    block.set_parameter(param_name, param_value)

        return workflow

    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate parameters against template inputs.

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Check required parameters
        for input_param in self.inputs:
            if input_param.required and input_param.name not in parameters:
                errors.append(f"Missing required parameter: {input_param.label}")

        # Check parameter types
        for input_param in self.inputs:
            if input_param.name in parameters:
                value = parameters[input_param.name]

                # Type validation
                if input_param.type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"{input_param.label} must be a number")
                elif input_param.type == "boolean" and not isinstance(value, bool):
                    errors.append(f"{input_param.label} must be a boolean")
                elif input_param.type == "list" and not isinstance(value, list):
                    errors.append(f"{input_param.label} must be a list")

                # Options validation
                if input_param.options and value not in input_param.options:
                    errors.append(
                        f"{input_param.label} must be one of: {', '.join(input_param.options)}"
                    )

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "difficulty": self.difficulty,
            "author": self.author,
            "version": self.version,
            "tags": self.tags,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "outputs": self.outputs,
            "workflow": self.workflow.to_dict() if self.workflow else None,
            "icon": self.icon,
            "preview_image": self.preview_image,
            "documentation_url": self.documentation_url,
            "downloads": self.downloads,
            "rating": self.rating,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """Create template from dictionary."""
        inputs = [TemplateInput.from_dict(inp) for inp in data.get("inputs", [])]

        workflow = None
        if data.get("workflow"):
            workflow = Workflow.from_dict(data["workflow"])

        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=data["category"],
            difficulty=data.get("difficulty", "easy"),
            author=data.get("author", ""),
            version=data.get("version", "1.0"),
            tags=data.get("tags", []),
            inputs=inputs,
            outputs=data.get("outputs", []),
            workflow=workflow,
            icon=data.get("icon", "📄"),
            preview_image=data.get("preview_image"),
            documentation_url=data.get("documentation_url"),
            downloads=data.get("downloads", 0),
            rating=data.get("rating", 0.0),
        )

    def save(self, file_path: Path):
        """Save template to file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, file_path: Path) -> "Template":
        """Load template from file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        return f"Template(id={self.id}, name={self.name}, category={self.category})"
