from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import QtGui

from guitools.gui import resize_elements

class MainWindow(QMainWindow):
    def __init__(self, gui):
        super().__init__()

        self.gui = gui

        # Determine resize factor for high-res screens
        screen = QApplication.primaryScreen()
        if screen.size().width()>2500:
            self.gui.resize_factor = 1.4
        elif screen.size().width()>1200:
            self.gui.resize_factor = 1.4
        else:
            self.gui.resize_factor = 1.0

        self.set_window()
#        self.add_toolbar()

    def resizeEvent(self, event):
        resize_elements(self.gui.config["element"], self.gui.central_widget, self.gui.resize_factor)

    def closeEvent(self,event):
        QApplication.quit()        

    def set_window(self):
        # Window size
        self.setWindowTitle(self.gui.config["window"]["title"])
        self.window_width = int(self.gui.config["window"]["width"]*self.gui.resize_factor)
        self.window_height = int(self.gui.config["window"]["height"]*self.gui.resize_factor)
        self.setMinimumSize(self.window_width, self.window_height)
        if self.gui.config["window"]["icon"]:
          self.setWindowIcon(QtGui.QIcon(self.gui.config["window"]["icon"]))

        screen = QApplication.primaryScreen()

        self.setGeometry(int(0.5*(screen.size().width() - self.window_width)),
                         int(0.5*(screen.size().height() - self.window_height)),
                         self.window_width,
                         self.window_height)

    def add_toolbar(self):
        pass
