"""Menu bar items: parsing YAML menu definitions into framework-specific menu actions."""

import importlib
from typing import Any, List, Optional

from guitares.dependencies import Dependency, DependencyCheck


class Text:
    """Reference to a GUI variable that provides dynamic menu text.

    Parameters
    ----------
    variable_group : str
        Default variable group for the text variable.
    """

    def __init__(self, variable_group: str) -> None:
        self.variable: str = ""
        self.variable_group: str = variable_group


class Menu:
    """A single menu or submenu item parsed from a YAML configuration dictionary.

    Parameters
    ----------
    dct : dict
        Dictionary describing the menu item (from YAML config).
    parent : Any
        Parent menu or window that contains this item.
    """

    def __init__(self, dct: dict, parent: Any) -> None:
        self.style: Optional[str] = None
        self.menus: List["Menu"] = []
        self.dependencies: List[Dependency] = []
        self.parent: Any = parent
        self.text: Any = ""
        self.option: Optional[str] = None
        self.checkable: bool = False
        self.separator: bool = False
        self.visible: bool = True
        self.enable: bool = True
        self.id: str = ""
        self.variable_group: str = parent.variable_group
        self.variable: Optional[str] = None
        self.module: Any = parent.module
        self.method: Any = ""
        self.callback: Any = None
        self.gui: Any = parent.gui
        self.getvar = parent.gui.getvar
        self.setvar = parent.gui.setvar
        self.icon: str = ""

        # Now update element attributes based on dict

        if "variable_group" in dct:
            self.variable_group = dct["variable_group"]
        if "id" in dct:
            self.id = dct["id"]
        if "option" in dct:
            self.option = dct["option"]
        if "checkable" in dct:
            self.checkable = dct["checkable"]
        if "variable" in dct:
            self.variable = dct["variable"]
        if "separator" in dct:
            self.separator = dct["separator"]
        if "module" in dct:
            if isinstance(dct["module"], str):
                try:
                    self.module = importlib.import_module(dct["module"])
                except Exception:
                    print(f"Error! Could not import module {dct['module']}")
        if "method" in dct:
            self.method = dct["method"]
            # Check if self.method is a string or a method
            if isinstance(self.method, str):
                if self.module:
                    if hasattr(self.module, self.method):
                        self.callback = getattr(self.module, self.method)
                    else:
                        print(f"Error! Could not find method {self.method}")
            else:
                # It's already a method
                self.callback = self.method
        if "text" in dct:
            if isinstance(dct["text"], dict):
                self.text = Text(self.variable_group)
                if "variable" in dct:
                    self.text.variable(dct["variable"])
                if "variable_group" in dct:
                    self.text.variable_group(dct["variable_group"])
            else:
                self.text = dct["text"]

        if "dependency" in dct:
            for dep in dct["dependency"]:
                dependency = Dependency()
                dependency.gui = parent.gui
                if "action" in dep:
                    dependency.action = dep["action"]
                if "checkfor" in dep:
                    dependency.checkfor = dep["checkfor"]
                for check_dct in dep["check"]:
                    check = DependencyCheck(self.variable_group)
                    if "variable" in check_dct:
                        check.variable = check_dct["variable"]
                    if "variable_group" in check_dct:
                        check.variable_group = check_dct["variable_group"]
                    if "operator" in check_dct:
                        check.operator = check_dct["operator"]
                    if "value" in check_dct:
                        check.value = check_dct["value"]
                    dependency.checks.append(check)
                self.dependencies.append(dependency)

    def add(self, has_children: bool = False) -> None:
        """Create the framework-specific menu widget (submenu or action).

        Parameters
        ----------
        has_children : bool, optional
            If ``True``, create a submenu instead of a leaf action.
        """
        mod = importlib.import_module(f"guitares.{self.gui.framework}.menu")
        if self.menus or has_children:
            # Submenu
            mod.Menu(self)
        else:
            # End node
            mod.Action(self)

    def set_dependencies(self) -> None:
        """Evaluate and apply dependency rules (enable/check) for this menu item."""
        for dependency in self.dependencies:
            okay = dependency.get()
            if dependency.action == "enable":
                if okay:
                    self.widget.setEnabled(True)
                else:
                    self.widget.setEnabled(False)
            elif dependency.action == "check":
                if okay:
                    self.widget.setChecked(True)
                else:
                    self.widget.setChecked(False)
