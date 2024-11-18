from PySide6.QtWidgets import QSplashScreen
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication
import os

class Splash:

    def __init__(self, splash_file, seconds=20.0):
        # Splash screen
        QSplashScreen(QPixmap(splash_file))
        self.splash = QSplashScreen(QPixmap(splash_file), Qt.WindowStaysOnTopHint)
        self.splash.show()
        # Close SplashScreen after 20 seconds (20,000 ms)
        QTimer.singleShot(int(seconds*1000), self.splash.close)

    def close(self):
        self.splash.close()
