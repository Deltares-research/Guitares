"""PyQt5 push button that opens a file-open dialog."""

import os
import traceback
from typing import Any

from PyQt5.QtWidgets import QFileDialog, QPushButton


class PushOpenFile(QPushButton):
    """Button that opens a file selection dialog and stores the chosen path.

    Parameters
    ----------
    element : Any
        The GUI element descriptor with variable binding, filter, title, and callback.
    """

    def __init__(self, element: Any) -> None:
        super().__init__("", element.parent.widget)

        self.element = element

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

        self.setVisible(True)

        self.clicked.connect(self.callback)

        self.set_geometry()

    def set(self) -> None:
        """Update button text and tooltip from bound variables."""
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

    def callback(self) -> None:
        """Open a file dialog and invoke the element callback with the selected path."""
        self.okay = True
        group = self.element.variable_group
        name = self.element.variable
        val = self.element.getvar(group, name)
        if not val:
            val = os.getcwd()

        if self.element.filter:
            if isinstance(self.element.filter, str):
                fltr = self.element.filter
            else:
                fltr = self.element.getvar(
                    self.element.filter.variable_group, self.element.filter.variable
                )
        else:
            fltr = "All Files (*)"

        fname = QFileDialog.getOpenFileName(self, self.element.title, val, fltr)

        if len(fname[0]) > 0:
            self.element.setvar(group, name, fname[0])
        else:
            self.okay = False

        try:
            if self.okay and self.element.callback:
                val = fname[0]
                self.element.callback(val, self)
                # Update GUI
                self.element.window.update()
        except Exception:
            traceback.print_exc()

    def set_geometry(self) -> None:
        """Set widget position and size from the element descriptor."""
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
