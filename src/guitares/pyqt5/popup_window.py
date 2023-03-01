from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtGui

class PopupWindow(QDialog):
    def __init__(self, window, modal=True):
        super().__init__()

        self.window = window

        # Determine resize factor for high-res screens
        screen = QApplication.primaryScreen()
        if screen.size().width()>2500:
            self.window.gui.resize_factor = 1.4
        elif screen.size().width()>1200:
            self.window.gui.resize_factor = 1.4
        else:
            self.window.gui.resize_factor = 1.0

        # Window size
        self.setWindowTitle(self.window.title)
        self.window_width = int(self.window.width*self.window.gui.resize_factor)
        self.window_height = int(self.window.height*self.window.gui.resize_factor)
        self.setMinimumSize(self.window_width, self.window_height)
        if self.window.icon:
          self.setWindowIcon(QtGui.QIcon(self.window.icon))
        screen = QApplication.primaryScreen()
        self.setGeometry(int(0.5*(screen.size().width() - self.window_width)),
                         int(0.5*(screen.size().height() - self.window_height)),
                         self.window_width,
                         self.window_height)

        self.setModal(modal)

    def resizeEvent(self, event):
        self.window.resize_elements(self.window.elements)
