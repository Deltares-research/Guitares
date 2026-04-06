"""PyQt5 status bar widget with configurable text fields."""

from typing import Any

from PyQt5.QtWidgets import QLabel, QStatusBar


class StatusBar:
    """Status bar with named text fields at the bottom of a window.

    Parameters
    ----------
    window : Any
        The parent window containing ``window_widget`` and ``statusbar_fields``.
    """

    def __init__(self, window: Any) -> None:
        self.parent = window.window_widget
        sb = QStatusBar()
        self.parent.setStatusBar(sb)
        self.widget = sb
        field_list = window.statusbar_fields
        self.field: dict[str, QLabel] = {}
        for field in field_list:
            id = field["id"]
            w = field["width"]
            text = field["text"]
            label = QLabel(text)
            self.field[id] = label
            sb.addPermanentWidget(label, w)

    def set_geometry(self) -> None:
        """Recalculate geometry (currently a no-op)."""
        return

    def show_message(self, message: str, time: int) -> None:
        """Display a temporary message in the status bar.

        Parameters
        ----------
        message : str
            The message text to display.
        time : int
            Duration in milliseconds to show the message.
        """
        self.widget.showMessage(message, time)

    def set_text(self, id: str, text: str) -> None:
        """Set text for a named status bar field.

        Parameters
        ----------
        id : str
            The field identifier.
        text : str
            The text to display.
        """
        self.field[id].setText(text)
