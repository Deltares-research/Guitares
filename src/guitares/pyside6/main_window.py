"""PySide6 main application window for the Guitares framework."""

from typing import Any

from PySide6 import QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


class MainWindow(QMainWindow):
    """Main application window that auto-scales elements based on screen DPI.

    Parameters
    ----------
    window : Any
        The Guitares window object describing size, title, and icon.
    """

    def __init__(self, window: Any) -> None:
        super().__init__()

        self.window = window

        # Determine resize factor for elements (fonts get scaled automatically)
        screen = QApplication.primaryScreen()

        # Create a QLabel widget
        qw = QWidget()
        qw.setVisible(False)
        qw.setGeometry(0, 0, 1, 1)
        qw.show()
        pt = qw.font().pointSize()
        font = QtGui.QFont("times", pt)
        fm = QtGui.QFontMetrics(font)
        height_in_pixels = fm.height()
        resize_factor = height_in_pixels / 11
        self.window.gui.resize_factor = resize_factor

        # Window size
        screen_width = screen.size().width()
        screen_height = screen.size().height()
        self.setWindowTitle(self.window.title)
        self.window_width = min(
            screen_width - 100, int(self.window.width * self.window.gui.resize_factor)
        )
        self.window_height = min(
            screen_height - 100, int(self.window.height * self.window.gui.resize_factor)
        )
        min_width = min(
            screen_width - 100,
            int(self.window.minimum_width * self.window.gui.resize_factor),
        )
        min_height = min(
            screen_height - 100,
            int(self.window.minimum_height * self.window.gui.resize_factor),
        )
        self.setMinimumSize(min_width, min_height)
        if self.window.icon:
            self.setWindowIcon(QtGui.QIcon(self.window.icon))
        self.setGeometry(
            int(0.5 * (screen_width - self.window_width)),
            int(0.5 * (screen_height - self.window_height)),
            self.window_width,
            self.window_height,
        )
        if self.window.fixed_size:
            self.setFixedSize(self.window_width, self.window_height)

    def resizeEvent(self, event: Any) -> None:
        """Resize child elements and status bar when the window is resized.

        Parameters
        ----------
        event : Any
            The Qt resize event.
        """
        self.window.resize_elements(self.window.elements)
        if self.window.statusbar:
            self.window.statusbar.set_geometry()

    def closeEvent(self, event: Any) -> None:
        """Quit the application when the main window is closed.

        Parameters
        ----------
        event : Any
            The Qt close event.
        """
        QApplication.quit()
