"""PyQt5 menu bar and menu action widgets."""

import traceback
from typing import Any, Optional


class Menu:
    """A menu entry in the menu bar.

    Parameters
    ----------
    menu : Any
        The menu descriptor with text, parent widget, and separator flag.
    """

    def __init__(self, menu: Any) -> None:
        menu.widget = menu.parent.widget.addMenu(f"&{menu.text}")
        if menu.separator:
            menu.parent.widget.addSeparator()


class Action:
    """A clickable menu action item.

    Parameters
    ----------
    menu : Any
        The action descriptor with text, callback, option, checkable flag,
        and variable binding.
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

    def menu_item_selected(self, callback: Any, option: Optional[str]) -> None:
        """Handle menu item selection, updating variables and invoking the callback.

        Parameters
        ----------
        callback : Any
            The callback function to invoke.
        option : str, optional
            The option string to pass to the callback.
        """
        try:
            # Check if widget is checkable
            if self.menu.checkable:
                checked = self.menu.widget.isChecked()
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
