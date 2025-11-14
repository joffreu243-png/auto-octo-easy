"""
Data extraction and manipulation blocks.

Blocks for extracting text, attributes, storing variables, etc.
"""

from typing import Dict, Any
from loguru import logger

from src.nodes.blocks.base import BaseBlock


class ExtractTextBlock(BaseBlock):
    """Extract text from element."""

    def __init__(self) -> None:
        """Initialize ExtractText block."""
        super().__init__(
            title="Extract Text",
            block_type="data",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")
        self.set_param("variable_name", "extracted_text")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute extract text action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            actions = browser.get_actions() if browser else None
            if not actions:
                raise Exception("Browser actions not available")

            selector = self.get_param("selector")
            if not selector:
                raise Exception("Selector is required")

            variable_name = self.get_param("variable_name", "extracted_text")

            logger.info(f"Extracting text from: {selector}")

            result = await actions.get_text(selector)

            if result.success:
                text = result.data.get("text", "")

                # Store in context variables
                if "variables" not in context:
                    context["variables"] = {}
                context["variables"][variable_name] = text

                self._executed = True
                self._result = {"success": True, "text": text, "variable": variable_name}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Extract text failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"ExtractText block error: {e}")
            raise


class ExtractAttributeBlock(BaseBlock):
    """Extract attribute from element."""

    def __init__(self) -> None:
        """Initialize ExtractAttribute block."""
        super().__init__(
            title="Extract Attribute",
            block_type="data",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")
        self.set_param("attribute", "href")
        self.set_param("variable_name", "extracted_attr")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute extract attribute action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            actions = browser.get_actions() if browser else None
            if not actions:
                raise Exception("Browser actions not available")

            selector = self.get_param("selector")
            attribute = self.get_param("attribute", "href")

            if not selector:
                raise Exception("Selector is required")

            variable_name = self.get_param("variable_name", "extracted_attr")

            logger.info(f"Extracting attribute '{attribute}' from: {selector}")

            result = await actions.get_attribute(selector, attribute)

            if result.success:
                value = result.data.get("value", "")

                # Store in context variables
                if "variables" not in context:
                    context["variables"] = {}
                context["variables"][variable_name] = value

                self._executed = True
                self._result = {"success": True, "value": value, "variable": variable_name}
                return self._result
            else:
                self._error = result.error
                raise Exception(f"Extract attribute failed: {result.error}")

        except Exception as e:
            self._error = str(e)
            logger.error(f"ExtractAttribute block error: {e}")
            raise


class SetVariableBlock(BaseBlock):
    """Set variable value."""

    def __init__(self) -> None:
        """Initialize SetVariable block."""
        super().__init__(
            title="Set Variable",
            block_type="data",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("variable_name", "my_var")
        self.set_param("value", "")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute set variable action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            variable_name = self.get_param("variable_name", "my_var")
            value = self.get_param("value", "")

            logger.info(f"Setting variable: {variable_name} = {value}")

            # Store in context variables
            if "variables" not in context:
                context["variables"] = {}
            context["variables"][variable_name] = value

            self._executed = True
            self._result = {"success": True, "variable": variable_name, "value": value}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"SetVariable block error: {e}")
            raise


class GetVariableBlock(BaseBlock):
    """Get variable value."""

    def __init__(self) -> None:
        """Initialize GetVariable block."""
        super().__init__(
            title="Get Variable",
            block_type="data",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("variable_name", "my_var")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get variable action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            variable_name = self.get_param("variable_name", "my_var")

            # Get from context variables
            variables = context.get("variables", {})
            value = variables.get(variable_name, None)

            logger.info(f"Getting variable: {variable_name} = {value}")

            self._executed = True
            self._result = {"success": True, "variable": variable_name, "value": value}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"GetVariable block error: {e}")
            raise


class ExtractMultipleBlock(BaseBlock):
    """Extract multiple elements (list)."""

    def __init__(self) -> None:
        """Initialize ExtractMultiple block."""
        super().__init__(
            title="Extract Multiple",
            block_type="data",
            num_inputs=1,
            num_outputs=1,
        )

        # Default parameters
        self.set_param("selector", "")
        self.set_param("attribute", "textContent")
        self.set_param("variable_name", "extracted_list")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute extract multiple action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            browser = context.get("browser")
            page = browser.current_page if browser else None
            if not page:
                raise Exception("No active page")

            selector = self.get_param("selector")
            if not selector:
                raise Exception("Selector is required")

            attribute = self.get_param("attribute", "textContent")
            variable_name = self.get_param("variable_name", "extracted_list")

            logger.info(f"Extracting multiple: {selector}")

            # Get all matching elements
            elements = await page.query_selector_all(selector)

            values = []
            for element in elements:
                if attribute == "textContent":
                    value = await element.text_content()
                else:
                    value = await element.get_attribute(attribute)
                values.append(value)

            # Store in context variables
            if "variables" not in context:
                context["variables"] = {}
            context["variables"][variable_name] = values

            self._executed = True
            self._result = {
                "success": True,
                "values": values,
                "count": len(values),
                "variable": variable_name
            }
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"ExtractMultiple block error: {e}")
            raise
