"""PyQt5 static text label widget."""

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class Text(QLabel):
    """Static text label bound to a GUI element.

    Parameters
    ----------
    element : Any
        The GUI element descriptor containing position, text, and variable info.
    """

    def __init__(self, element: Any) -> None:
        super().__init__("", element.parent.widget)

        self.element = element

        self.setVisible(True)

        self.set_geometry()

        if self.element.text_position:
            self.setAlignment(Text.convert_to_qt_alignment(self.element.text_position))

    def set(self) -> None:
        """Update the displayed text from the bound variable or static text."""
        if self.element.variable:
            group = self.element.variable_group
            name = self.element.variable
            val = self.element.getvar(group, name)
        else:
            val = self.element.text
        self.setText(val)

    def set_geometry(self) -> None:
        """Set widget position and size from the element descriptor."""
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)

    @staticmethod
    def convert_to_qt_alignment(alignment_string: str) -> Qt.AlignmentFlag:
        """Convert a string alignment name to a Qt alignment flag.

        Parameters
        ----------
        alignment_string : str
            One of "left", "right", "top", "bottom", "top-left", "top-right",
            "bottom-left", "bottom-right", or "center".

        Returns
        -------
        Qt.AlignmentFlag
            The corresponding Qt alignment flag combination.
        """
        alignment_mapping = {
            "left": Qt.AlignLeft | Qt.AlignVCenter,
            "right": Qt.AlignRight | Qt.AlignVCenter,
            "top": Qt.AlignTop | Qt.AlignHCenter,
            "bottom": Qt.AlignBottom | Qt.AlignHCenter,
            "top-left": Qt.AlignTop | Qt.AlignLeft,
            "top-right": Qt.AlignTop | Qt.AlignRight,
            "bottom-left": Qt.AlignBottom | Qt.AlignLeft,
            "bottom-right": Qt.AlignBottom | Qt.AlignRight,
            "center": Qt.AlignCenter,
        }

        return alignment_mapping.get(alignment_string, Qt.AlignLeft | Qt.AlignVCenter)
