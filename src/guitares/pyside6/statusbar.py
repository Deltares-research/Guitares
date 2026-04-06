"""PySide6 status bar widget with multiple text fields."""

from typing import Any

from PySide6.QtWidgets import QLabel, QStatusBar


class StatusBar:
    """Status bar with named text fields displayed at the bottom of a window.

    Parameters
    ----------
    window : Any
        The Guitares window object that owns this status bar.
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
        """Reposition the status bar (currently a no-op)."""
        return

    def show_message(self, message: str, time: int) -> None:
        """Show a temporary message in the status bar.

        Parameters
        ----------
        message : str
            The message text to display.
        time : int
            Duration in milliseconds to show the message.
        """
        self.widget.showMessage(message, time)

    def set_text(self, id: str, text: str) -> None:
        """Set the text of a named status bar field.

        Parameters
        ----------
        id : str
            The field identifier.
        text : str
            The new text to display.
        """
        self.field[id].setText(text)
