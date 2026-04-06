"""PyQt5 splash screen with auto-close timer."""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen


class Splash:
    """Splash screen that displays an image and closes after a timeout.

    Parameters
    ----------
    splash_file : str
        Path to the splash screen image file.
    seconds : float
        Number of seconds before the splash screen auto-closes.
    """

    def __init__(self, splash_file: str, seconds: float = 20.0) -> None:
        QSplashScreen(QPixmap(splash_file))
        self.splash = QSplashScreen(QPixmap(splash_file), Qt.WindowStaysOnTopHint)
        self.splash.show()
        QTimer.singleShot(int(seconds * 1000), self.splash.close)

    def close(self) -> None:
        """Close the splash screen immediately."""
        self.splash.close()
