"""PySide6 popup (dialog) window for Guitares modal/non-modal dialogs."""

from typing import Any

from PySide6 import QtGui
from PySide6.QtWidgets import QApplication, QDialog


class PopupWindow(QDialog):
    """Resizable popup dialog window.

    Parameters
    ----------
    window : Any
        The Guitares window object describing size, title, and icon.
    modal : bool
        Whether the dialog should block input to other windows.
    """

    def __init__(self, window: Any, modal: bool = True) -> None:
        super().__init__()

        self.window = window

        # Determine resize factor for high-res screens
        screen = QApplication.primaryScreen()
        if screen.size().width() > 2500:
            self.window.gui.resize_factor = 1.4
        elif screen.size().width() > 1200:
            self.window.gui.resize_factor = 1.4
        else:
            self.window.gui.resize_factor = 1.0

        # Window size
        self.setWindowTitle(self.window.title)
        self.window_width = int(self.window.width * self.window.gui.resize_factor)
        self.window_height = int(self.window.height * self.window.gui.resize_factor)
        self.setMinimumSize(self.window_width, self.window_height)
        if self.window.icon:
            self.setWindowIcon(QtGui.QIcon(self.window.icon))
        screen = QApplication.primaryScreen()
        self.setGeometry(
            int(0.5 * (screen.size().width() - self.window_width)),
            int(0.5 * (screen.size().height() - self.window_height)),
            self.window_width,
            self.window_height,
        )

        self.setModal(modal)

    def resizeEvent(self, event: Any) -> None:
        """Resize child elements when the dialog is resized.

        Parameters
        ----------
        event : Any
            The Qt resize event.
        """
        self.window.resize_elements(self.window.elements)
