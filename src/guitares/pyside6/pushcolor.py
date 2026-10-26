"""PySide6 colour swatch button for Guitares GUI elements.

The button shows the colour stored in its variable (an RGB tuple with
values 0..1, or a hex string) and opens a colour dialog when clicked.
"""

import traceback
from typing import Any, Tuple, Union

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QColorDialog, QLabel, QPushButton

ColorValue = Union[Tuple[float, float, float], str]


def _to_qcolor(value: Any) -> QtGui.QColor:
    if isinstance(value, str):
        return QtGui.QColor(value)
    try:
        r, g, b = value[:3]
        return QtGui.QColor.fromRgbF(float(r), float(g), float(b))
    except Exception:
        return QtGui.QColor("white")


class PushColor(QPushButton):
    """Colour selection button that syncs its colour with a Guitares variable.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this button.
    """

    def __init__(self, element: Any) -> None:
        super().__init__("", element.parent.widget)

        self.element = element
        self.color = QtGui.QColor("white")

        if element.text:
            if isinstance(element.text, str):
                txt = element.text
            else:
                txt = self.element.getvar(
                    element.text.variable_group, element.text.variable
                )
            label = QLabel(txt, element.parent.widget)
            label.setStyleSheet("background: transparent; border: none")
            if not element.enable:
                label.setEnabled(False)
            self.text_widget = label
            label.setVisible(True)

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
        """Update the swatch colour from the linked variable."""
        if self.element.variable:
            val = self.element.getvar(
                self.element.variable_group, self.element.variable
            )
            if val is not None:
                self.color = _to_qcolor(val)
        self.setStyleSheet(f"QPushButton {{ background-color: {self.color.name()}; }}")
        if not isinstance(self.element.text, str) and hasattr(self, "text_widget"):
            self.text_widget.setText(
                self.element.getvar(
                    self.element.text.variable_group, self.element.text.variable
                )
            )

    def callback(self) -> None:
        """Open the colour dialog and store the chosen colour."""
        try:
            color = QColorDialog.getColor(self.color, self, "Select Colour")
            if not color.isValid():
                return
            self.color = color
            value = (color.redF(), color.greenF(), color.blueF())
            if self.element.variable:
                self.element.setvar(
                    self.element.variable_group, self.element.variable, value
                )
            self.setStyleSheet(f"QPushButton {{ background-color: {color.name()}; }}")
            if self.element.callback:
                self.element.callback(value, self)
            self.element.window.update()
        except Exception:
            traceback.print_exc()

    def set_geometry(self) -> None:
        """Position and size the button and its label."""
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        if self.element.text:
            txt = (
                self.element.text
                if isinstance(self.element.text, str)
                else self.element.getvar(
                    self.element.text.variable_group, self.element.text.variable
                )
            )
            label = self.text_widget
            fm = label.fontMetrics()
            wlab = int(fm.size(0, txt).width())
            if self.element.text_position in ("above-center", "above"):
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setGeometry(
                    x0, int(y0 - 20 * resize_factor), wdt, int(20 * resize_factor)
                )
            elif self.element.text_position == "above-left":
                label.setAlignment(QtCore.Qt.AlignLeft)
                label.setGeometry(
                    x0, int(y0 - 20 * resize_factor), wlab, int(20 * resize_factor)
                )
            elif self.element.text_position == "right":
                label.setAlignment(QtCore.Qt.AlignLeft)
                label.setGeometry(
                    int(x0 + wdt + 3 * resize_factor),
                    int(y0 + 5 * resize_factor),
                    wlab,
                    int(20 * resize_factor),
                )
            else:
                label.setAlignment(QtCore.Qt.AlignRight)
                label.setGeometry(
                    int(x0 - wlab - 3 * resize_factor),
                    int(y0 + 5 * resize_factor),
                    wlab,
                    int(20 * resize_factor),
                )
