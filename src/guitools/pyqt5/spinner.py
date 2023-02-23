from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
from pathlib import Path

from src.guitools.pyqt5.widget_group import WidgetGroup


class Spinner(WidgetGroup):
    def __init__(self, element, parent):
        super().__init__(element, parent)

        self.spinner = QWidget()

        self.spinner.setFixedSize(200, 200)
        self.spinner.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)

        self.spinner.label_animation = QLabel(self.spinner)

        self.movie = QMovie('loading.gif')
        self.spinner.label_animation.setMovie(self.movie)

        # timer = QTimer(self.spinner)
        # self.start
        # timer.singleShot(3000, self.stop)

        self.widgets.append(self.spinner)

    def start(self):
        self.movie.start()
        self.spinner.show()

    def stop(self):
        self.movie.stop()
        self.spinner.close()
