"""PySide6 multi-line text editor widget wrapper for Guitares GUI elements."""

import traceback
from typing import Any, Optional

from PySide6 import QtCore
from PySide6.QtWidgets import QLabel, QPlainTextEdit


class TextEdit(QPlainTextEdit):
    """Multi-line plain text editor that syncs its text with a Guitares variable.

    The variable is updated and the element callback fired when the widget
    loses focus (like a MATLAB multi-line edit control).

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this editor.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)

        self.element = element
        self.string: Optional[str] = None

        if not element.enable:
            self.setEnabled(False)

        self.setVisible(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

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

        self.set_geometry()

    def set(self) -> None:
        """Update the editor text from the linked variable."""
        group = self.element.variable_group
        name = self.element.variable
        val = self.element.getvar(group, name)
        if val is None:
            val = ""
        self.string = str(val)
        if self.toPlainText() != self.string:
            self.setPlainText(self.string)
        self.setStyleSheet("")

        if not isinstance(self.element.text, str):
            txt = self.element.getvar(
                self.element.text.variable_group, self.element.text.variable
            )
            self.text_widget.setText(txt)

        if not isinstance(self.element.tooltip, str):
            txt = self.element.getvar(
                self.element.tooltip.variable_group, self.element.tooltip.variable
            )
            self.setToolTip(txt)

    def focusOutEvent(self, event: Any) -> None:  # noqa: N802
        """Commit the text when the widget loses focus."""
        super().focusOutEvent(event)
        self.callback()

    def callback(self) -> None:
        """Commit the edited text and fire the element callback."""
        newtext = self.toPlainText()
        if newtext == self.string:
            return
        group = self.element.variable_group
        name = self.element.variable
        oldval = self.element.getvar(group, name)
        self.element.setvar(group, name, newtext)
        self.string = newtext
        try:
            if self.isEnabled() and self.element.callback:
                self.element.callback(newtext, self)
            self.element.window.update()
        except Exception as e:
            traceback.print_exc()
            self.element.setvar(group, name, oldval)
            try:
                self.element.window.dialog_warning(str(e))
            except Exception:
                pass
            self.element.window.update()

    def set_geometry(self) -> None:
        """Position and size the editor and its label."""
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        if self.element.text:
            if not isinstance(self.element.text, str):
                txt = self.element.getvar(
                    self.element.text.variable_group, self.element.text.variable
                )
            else:
                txt = self.element.text
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
                    x0, int(y0 - 15 * resize_factor), wlab, int(20 * resize_factor)
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
