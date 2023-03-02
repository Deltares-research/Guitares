# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.
#
# This tool is developed for demonstration purposes only.

from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap


class Splash:

    def __init__(self, splash_file, seconds=20.0):

        # Splash screen
        QSplashScreen(QPixmap(splash_file))
        self.splash = QSplashScreen(QPixmap(splash_file))
        self.splash.show()
        # Close SplashScreen after 20 seconds (20,000 ms)
        QTimer.singleShot(int(seconds*1000), self.splash.close)

    def close(self):
        self.splash.close()
