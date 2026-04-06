"""PySide6 splash screen widget for application startup."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSplashScreen


class Splash:
    """Splash screen that auto-closes after a timeout.

    Parameters
    ----------
    splash_file : str
        Path to the splash screen image file.
    seconds : float
        Number of seconds before the splash screen auto-closes.
    """

    def __init__(self, splash_file: str, seconds: float = 20.0) -> None:
        # Splash screen
        QSplashScreen(QPixmap(splash_file))
        self.splash = QSplashScreen(QPixmap(splash_file), Qt.WindowStaysOnTopHint)
        self.splash.show()
        # Close SplashScreen after timeout
        QTimer.singleShot(int(seconds * 1000), self.splash.close)

    def close(self) -> None:
        """Close the splash screen immediately."""
        self.splash.close()
