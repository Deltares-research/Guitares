"""PySide6 push button that opens a save-file dialog."""

import os
import traceback
from typing import Any

from PySide6.QtWidgets import QFileDialog, QPushButton


class PushSaveFile(QPushButton):
    """Button that opens a save-file dialog and stores the selected path.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this button.
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
        """Update button text and tooltip from the linked variables."""
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
        """Open the save-file dialog and fire the element callback."""
        self.okay = True
        group = self.element.variable_group
        name = self.element.variable
        val = self.element.getvar(group, name)
        if not val:
            val = os.getcwd()
        fname = QFileDialog.getSaveFileName(
            self, self.element.title, val, self.element.filter
        )

        if self.element.full_path:
            filename = fname[0]
        else:
            # Check if the path is different from the current path
            curdir = os.getcwd().replace("\\", "/")
            if os.path.dirname(fname[0]) != curdir:
                # Different path so use full path
                filename = fname[0]
            else:
                # Same path so use only the filename
                filename = os.path.basename(fname[0])

        if len(filename) > 0:
            self.element.setvar(group, name, filename)
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
        """Position and size the button."""
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
