"""PySide6 menu and menu action wrappers for Guitares menu bar items."""

import traceback
from typing import Any, Callable, Optional


class Menu:
    """Top-level or sub-menu entry in the menu bar.

    Parameters
    ----------
    menu : Any
        The Guitares menu descriptor.
    """

    def __init__(self, menu: Any) -> None:
        menu.widget = menu.parent.widget.addMenu(f"&{menu.text}")
        if menu.separator:
            menu.parent.widget.addSeparator()


class Action:
    """Clickable menu action item, optionally checkable.

    Parameters
    ----------
    menu : Any
        The Guitares menu descriptor for this action.
    """

    def __init__(self, menu: Any) -> None:
        menu.widget = menu.parent.widget.addAction(f"&{menu.text}")
        self.menu = menu
        if menu.checkable:
            menu.widget.setCheckable(True)
        if menu.callback:
            menu.widget.triggered.connect(
                lambda state, f=menu.callback, o=menu.option: self.menu_item_selected(
                    f, o
                )
            )
        if menu.separator:
            menu.parent.widget.addSeparator()

    def menu_item_selected(self, callback: Callable, option: Optional[str]) -> None:
        """Handle menu item selection, updating check state and firing the callback.

        Parameters
        ----------
        callback : Callable
            The function to call when this item is selected.
        option : Optional[str]
            The option string associated with this menu item.
        """
        try:
            # Check if widget is checkable
            if self.menu.checkable:
                # Check if widget is checked
                if self.menu.widget.isChecked():
                    checked = True
                else:
                    checked = False
                # If there is a variable, set it
                if self.menu.variable_group and self.menu.variable:
                    self.menu.setvar(
                        self.menu.variable_group, self.menu.variable, checked
                    )
            # Should change this so that it always sends option and checked?
            if self.menu.variable_group and self.menu.variable:
                callback(option, checked)
            else:
                callback(option)
        except Exception:
            traceback.print_exc()
