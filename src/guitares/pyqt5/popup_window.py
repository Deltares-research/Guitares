"""PyQt5 popup (dialog) window with automatic sizing for high-res screens."""

from typing import Any

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QDialog


class PopupWindow(QDialog):
    """Modal or modeless popup dialog window.

    Parameters
    ----------
    window : Any
        The parent window descriptor with title, size, icon, and GUI reference.
    modal : bool
        Whether the dialog should be modal.
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
        """Handle window resize by updating child element positions.

        Parameters
        ----------
        event : Any
            The resize event.
        """
        self.window.resize_elements(self.window.elements)
