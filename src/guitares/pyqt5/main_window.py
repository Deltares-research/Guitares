from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import QtGui
import os

class MainWindow(QMainWindow):
    def __init__(self, window):
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
        self.setWindowTitle(self.window.title)
        self.window_width = int(self.window.width*self.window.gui.resize_factor)
        self.window_height = int(self.window.height*self.window.gui.resize_factor)
        min_width = int(self.window.minimum_width*self.window.gui.resize_factor)
        min_height = int(self.window.minimum_height*self.window.gui.resize_factor)
        self.setMinimumSize(min_width, min_height)
        if self.window.icon:
          self.setWindowIcon(QtGui.QIcon(self.window.icon))
        # screen = QApplication.primaryScreen()
        self.setGeometry(int(0.5*(screen.size().width() - self.window_width)),
                         int(0.5*(screen.size().height() - self.window_height)),
                         self.window_width,
                         self.window_height)
        if self.window.fixed_size:
            self.setFixedSize(self.window_width, self.window_height)

    def resizeEvent(self, event):
        self.window.resize_elements(self.window.elements)
        if self.window.statusbar:
            self.window.statusbar.set_geometry()

    def closeEvent(self, event):
        QApplication.quit()        

