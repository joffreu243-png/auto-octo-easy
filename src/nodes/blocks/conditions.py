"""
Control flow blocks for workflow execution.

Blocks for conditional execution, loops, and branching logic.
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from src.nodes.blocks.base import BaseBlock


class IfBlock(BaseBlock):
    """Conditional execution block."""

    def __init__(self) -> None:
        """Initialize If block."""
        super().__init__(
            title="If Condition",
            block_type="condition",
            num_inputs=1,
            num_outputs=2,  # True path, False path
        )

        # Default parameters
        self.set_param("condition_type", "variable")  # variable, expression, element_exists
        self.set_param("variable_name", "")
        self.set_param("operator", "==")  # ==, !=, >, <, >=, <=, contains, exists
        self.set_param("compare_value", "")
        self.set_param("selector", "")  # For element_exists condition

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute conditional check.

        Args:
            context: Execution context

        Returns:
            Execution result with branch_taken field
        """
        try:
            condition_type = self.get_param("condition_type", "variable")
            result = False

            if condition_type == "variable":
                result = await self._evaluate_variable_condition(context)
            elif condition_type == "expression":
                result = await self._evaluate_expression_condition(context)
            elif condition_type == "element_exists":
                result = await self._evaluate_element_exists(context)
            else:
                raise Exception(f"Unknown condition type: {condition_type}")

            logger.info(f"Condition evaluated to: {result}")

            self._executed = True
            self._result = {
                "success": True,
                "condition_met": result,
                "branch_taken": 0 if result else 1,  # 0 = true path, 1 = false path
            }
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"If block error: {e}")
            raise

    async def _evaluate_variable_condition(self, context: Dict[str, Any]) -> bool:
        """Evaluate variable condition.

        Args:
            context: Execution context

        Returns:
            Condition result
        """
        variable_name = self.get_param("variable_name")
        operator = self.get_param("operator", "==")
        compare_value = self.get_param("compare_value")

        variables = context.get("variables", {})
        actual_value = variables.get(variable_name)

        if actual_value is None:
            return operator == "exists" or operator == "!="

        # Convert compare_value to same type as actual_value if possible
        try:
            if isinstance(actual_value, (int, float)):
                compare_value = type(actual_value)(compare_value)
        except (ValueError, TypeError):
            pass

        if operator == "==":
            return actual_value == compare_value
        elif operator == "!=":
            return actual_value != compare_value
        elif operator == ">":
            return actual_value > compare_value
        elif operator == "<":
            return actual_value < compare_value
        elif operator == ">=":
            return actual_value >= compare_value
        elif operator == "<=":
            return actual_value <= compare_value
        elif operator == "contains":
            return str(compare_value) in str(actual_value)
        elif operator == "exists":
            return True
        else:
            raise Exception(f"Unknown operator: {operator}")

    async def _evaluate_expression_condition(self, context: Dict[str, Any]) -> bool:
        """Evaluate expression condition.

        Args:
            context: Execution context

        Returns:
            Condition result
        """
        # For safety, we use a limited expression evaluator
        # In production, this should use a proper expression parser
        expression = self.get_param("compare_value")
        variables = context.get("variables", {})

        # Simple variable substitution
        for var_name, var_value in variables.items():
            expression = expression.replace(f"{{{var_name}}}", str(var_value))

        try:
            # Very limited eval - only basic comparisons
            result = eval(expression, {"__builtins__": {}}, {})
            return bool(result)
        except Exception as e:
            logger.error(f"Expression evaluation failed: {e}")
            return False

    async def _evaluate_element_exists(self, context: Dict[str, Any]) -> bool:
        """Check if element exists on page.

        Args:
            context: Execution context

        Returns:
            True if element exists
        """
        browser = context.get("browser")
        page = browser.current_page if browser else None
        if not page:
            return False

        selector = self.get_param("selector")
        if not selector:
            return False

        try:
            element = await page.query_selector(selector)
            return element is not None
        except Exception:
            return False


class LoopBlock(BaseBlock):
    """Loop iteration block."""

    def __init__(self) -> None:
        """Initialize Loop block."""
        super().__init__(
            title="Loop",
            block_type="condition",
            num_inputs=1,
            num_outputs=2,  # Loop body, Exit
        )

        # Default parameters
        self.set_param("loop_type", "range")  # range, list, variable
        self.set_param("start", 0)
        self.set_param("end", 10)
        self.set_param("step", 1)
        self.set_param("variable_name", "")  # Variable containing list
        self.set_param("iterator_name", "i")  # Variable to store current item/index

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute loop initialization.

        Args:
            context: Execution context

        Returns:
            Execution result with loop info
        """
        try:
            loop_type = self.get_param("loop_type", "range")
            iterator_name = self.get_param("iterator_name", "i")

            items = []

            if loop_type == "range":
                start = int(self.get_param("start", 0))
                end = int(self.get_param("end", 10))
                step = int(self.get_param("step", 1))
                items = list(range(start, end, step))

            elif loop_type == "list":
                variable_name = self.get_param("variable_name")
                variables = context.get("variables", {})
                items = variables.get(variable_name, [])
                if not isinstance(items, list):
                    items = [items]

            elif loop_type == "variable":
                variable_name = self.get_param("variable_name")
                variables = context.get("variables", {})
                value = variables.get(variable_name)
                if isinstance(value, list):
                    items = value
                elif isinstance(value, (int, float)):
                    items = list(range(int(value)))
                else:
                    items = [value]

            logger.info(f"Loop initialized with {len(items)} items")

            # Store loop state in context
            if "loop_state" not in context:
                context["loop_state"] = {}

            loop_id = id(self)
            context["loop_state"][loop_id] = {
                "items": items,
                "current_index": 0,
                "iterator_name": iterator_name,
                "break_requested": False,
                "continue_requested": False,
            }

            self._executed = True
            self._result = {
                "success": True,
                "loop_id": loop_id,
                "total_items": len(items),
                "branch_taken": 0 if items else 1,  # 0 = loop body, 1 = exit
            }
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"Loop block error: {e}")
            raise


class SwitchBlock(BaseBlock):
    """Multi-way branching block."""

    def __init__(self) -> None:
        """Initialize Switch block."""
        super().__init__(
            title="Switch",
            block_type="condition",
            num_inputs=1,
            num_outputs=5,  # Case 1-4, Default
        )

        # Default parameters
        self.set_param("variable_name", "")
        self.set_param("case_1", "")
        self.set_param("case_2", "")
        self.set_param("case_3", "")
        self.set_param("case_4", "")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute switch evaluation.

        Args:
            context: Execution context

        Returns:
            Execution result with branch_taken field
        """
        try:
            variable_name = self.get_param("variable_name")
            variables = context.get("variables", {})
            value = variables.get(variable_name)

            # Check each case
            for i in range(1, 5):
                case_value = self.get_param(f"case_{i}")
                if case_value and str(value) == str(case_value):
                    logger.info(f"Switch matched case {i}: {case_value}")
                    self._executed = True
                    self._result = {
                        "success": True,
                        "matched_case": i,
                        "branch_taken": i - 1,  # 0-3 for cases 1-4
                    }
                    return self._result

            # Default case (output 4)
            logger.info("Switch using default case")
            self._executed = True
            self._result = {
                "success": True,
                "matched_case": "default",
                "branch_taken": 4,
            }
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"Switch block error: {e}")
            raise


class BreakBlock(BaseBlock):
    """Break out of loop block."""

    def __init__(self) -> None:
        """Initialize Break block."""
        super().__init__(
            title="Break Loop",
            block_type="condition",
            num_inputs=1,
            num_outputs=0,  # No outputs - terminates loop
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute break action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            logger.info("Break requested")

            # Signal break to executor
            if "control_flow" not in context:
                context["control_flow"] = {}

            context["control_flow"]["break"] = True

            self._executed = True
            self._result = {"success": True, "action": "break"}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"Break block error: {e}")
            raise


class ContinueBlock(BaseBlock):
    """Continue to next loop iteration."""

    def __init__(self) -> None:
        """Initialize Continue block."""
        super().__init__(
            title="Continue Loop",
            block_type="condition",
            num_inputs=1,
            num_outputs=0,  # No outputs - skips to next iteration
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute continue action.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        try:
            logger.info("Continue requested")

            # Signal continue to executor
            if "control_flow" not in context:
                context["control_flow"] = {}

            context["control_flow"]["continue"] = True

            self._executed = True
            self._result = {"success": True, "action": "continue"}
            return self._result

        except Exception as e:
            self._error = str(e)
            logger.error(f"Continue block error: {e}")
            raise
