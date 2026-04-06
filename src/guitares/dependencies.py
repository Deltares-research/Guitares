"""GUI element dependency checks for conditional visibility, enabling, and state."""

import traceback
from typing import Any, List


class DependencyCheck:
    """A single condition that compares a GUI variable against a target value.

    Parameters
    ----------
    variable_group : str
        Default variable group for the check.
    """

    def __init__(self, variable_group: str) -> None:
        self.variable: str = ""
        self.variable_group: str = variable_group
        self.operator: str = "eq"
        self.value: Any = None


class Dependency:
    """A collection of checks that determine an action (enable/visible) for a GUI element.

    Attributes
    ----------
    action : str
        The action to take: ``"enable"`` or ``"visible"``.
    checkfor : str
        Logic mode: ``"all"``, ``"any"``, or ``"none"``.
    checks : List[DependencyCheck]
        List of individual checks to evaluate.
    """

    def __init__(self) -> None:
        self.action: str = "enable"
        self.checkfor: str = "all"
        self.checks: List[DependencyCheck] = []
        self.gui: Any = None  # Must be set before calling get()

    def get(self) -> bool:
        """Evaluate all checks and return whether the dependency condition is met.

        Returns
        -------
        bool
            ``True`` if the combined checks satisfy the ``checkfor`` mode,
            ``False`` otherwise.  Returns ``False`` on any exception.
        """
        try:
            if self.gui is None:
                return False
            getvar = self.gui.getvar
            if self.checkfor == "all":
                okay = True
                for check in self.checks:
                    name = check.variable
                    group = check.variable_group
                    value = getvar(group, name)
                    if isinstance(check.value, dict):
                        check_value = getvar(
                            check.value.variable_group, check.value.variable
                        )
                    else:
                        check_value = check.value
                        if isinstance(value, int):
                            check_value = int(check_value)
                        elif isinstance(value, float):
                            check_value = float(check_value)
                    if check.operator == "eq":
                        if value != check_value:
                            okay = False
                            break
                    elif check.operator == "ne":
                        if value == check_value:
                            okay = False
                            break
                    elif check.operator == "gt":
                        if value <= check_value:
                            okay = False
                            break
                    elif check.operator == "ge":
                        if value < check_value:
                            okay = False
                            break
                    elif check.operator == "lt":
                        if value >= check_value:
                            okay = False
                            break
                    elif check.operator == "le":
                        if value > check_value:
                            okay = False
                            break
            elif self.checkfor == "any":
                okay = False
                for check in self.checks:
                    name = check.variable
                    group = check.variable_group
                    value = getvar(group, name)
                    if isinstance(check.value, dict):
                        check_value = getvar(
                            check.value.variable_group, check.value.variable
                        )
                    else:
                        check_value = check.value
                        if isinstance(value, int):
                            check_value = int(check_value)
                        elif isinstance(value, float):
                            check_value = float(check_value)
                    if check.operator == "eq":
                        if value == check_value:
                            okay = True
                            break
                    elif check.operator == "ne":
                        if value != check_value:
                            okay = True
                            break
                    elif check.operator == "gt":
                        if value > check_value:
                            okay = True
                            break
                    elif check.operator == "ge":
                        if value >= check_value:
                            okay = True
                            break
                    elif check.operator == "lt":
                        if value < check_value:
                            okay = True
                            break
                    elif check.operator == "le":
                        if value <= check_value:
                            okay = True
                            break
            elif self.checkfor == "none":
                okay = True
                for check in self.checks:
                    name = check.variable
                    group = check.variable_group
                    value = getvar(group, name)
                    if isinstance(check.value, dict):
                        check_value = getvar(
                            check.value.variable_group, check.value.variable
                        )
                    else:
                        check_value = check.value
                        if isinstance(value, int):
                            check_value = int(check_value)
                        elif isinstance(value, float):
                            check_value = float(check_value)
                    if check.operator == "eq":
                        if value == check_value:
                            okay = False
                            break
                    elif check.operator == "ne":
                        if value != check_value:
                            okay = False
                            break
                    elif check.operator == "gt":
                        if value > check_value:
                            okay = False
                            break
                    elif check.operator == "ge":
                        if value >= check_value:
                            okay = False
                            break
                    elif check.operator == "lt":
                        if value < check_value:
                            okay = False
                            break
                    elif check.operator == "le":
                        if value <= check_value:
                            okay = False
                            break
            return okay

        except Exception:
            traceback.print_exc()
            return False
