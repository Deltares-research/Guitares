"""PyQt5 checkbox widget bound to a GUI variable."""

import logging
from typing import Any

from PyQt5.QtWidgets import QCheckBox

logger = logging.getLogger(__name__)


class CheckBox(QCheckBox):
    """Checkbox widget that reads/writes a boolean GUI variable.

    Parameters
    ----------
    element : Any
        The GUI element descriptor with variable binding and callback info.
    """

    def __init__(self, element: Any) -> None:
        super().__init__("", element.parent.widget)

        self.element = element

        self.setVisible(True)

        if element.text:
            if isinstance(element.text, str):
                txt = element.text
            else:
                txt = self.element.getvar(
                    element.text.variable_group, element.text.variable
                )
            self.setText(txt)

        if self.element.tooltip:
            if isinstance(self.element.tooltip, str):
                txt = self.element.tooltip
            else:
                txt = self.element.getvar(
                    self.element.tooltip.variable_group, self.element.tooltip.variable
                )
            self.setToolTip(txt)

        self.clicked.connect(self.callback)

        self.set_geometry()

    def set(self) -> None:
        """Update the checkbox state from the bound variable."""
        group = self.element.variable_group
        name = self.element.variable
        val = self.element.getvar(group, name)
        if val is True:
            self.setChecked(True)
        else:
            self.setChecked(False)

        if not isinstance(self.element.text, str):
            self.setText(
                self.element.getvar(
                    self.element.text.variable_group, self.element.text.variable
                )
            )
        if not isinstance(self.element.tooltip, str):
            self.setToolTip(
                self.element.getvar(
                    self.element.tooltip.variable_group, self.element.tooltip.variable
                )
            )

    def callback(self, state: bool) -> None:
        """Handle checkbox click events.

        Parameters
        ----------
        state : bool
            The new checked state.
        """
        group = self.element.variable_group
        name = self.element.variable
        val = state
        self.element.setvar(group, name, val)
        try:
            if self.isEnabled() and self.element.callback:
                self.element.callback(val, self)
            # Update GUI
            self.element.window.update()
        except Exception as e:
            logger.exception(f"Error in CheckBox callback: {e}")

    def set_geometry(self) -> None:
        """Set widget position and size, adjusting width to fit text."""
        if self.element.id == "sbg":
            pass
        x0, y0, wdt, hgt = self.element.get_position()
        # Get the width of the text in pixels and add 25 pixels
        txt = self.text()
        wdt = self.fontMetrics().boundingRect(txt).width() + 25
        self.setGeometry(x0, y0, wdt, hgt)
