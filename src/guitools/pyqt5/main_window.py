from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QVBoxLayout

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()

#        QApplication.instance()
        screen = QApplication.primaryScreen()
        if screen.size().width()>2500:
            self.resize_factor = 2.0
        elif screen.size().width()>1200:
            self.resize_factor = 1.4
        else:
            self.resize_factor = 1.0

        self.config = config

        self.set_window()
        self.add_toolbar()
        
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.central_widget = widget

    def resizeEvent(self, event):
        self.resize_elements(self.config["element"], self.central_widget)

    def closeEvent(self,event):
        QApplication.quit()        

    def set_window(self):
        # Window size
        self.setWindowTitle(self.config["window"]["title"])
        self.window_width = int(self.config["window"]["width"]*self.resize_factor)
        self.window_height = int(self.config["window"]["height"]*self.resize_factor)
        self.setMinimumSize(self.window_width, self.window_height)

        screen = QApplication.primaryScreen()

        self.setGeometry(int(0.5*(screen.size().width() - self.window_width)),
                         int(0.5*(screen.size().height() - self.window_height)),
                         self.window_width,
                         self.window_height)

    def add_toolbar(self):
        pass

    def resize_elements(self, element_list, parent):
        for element in element_list:
            if element["style"] == "tabpanel":
                tab_panel = element["widget"]
                x0, y0, wdt, hgt = self.get_position_from_string(element["position"], parent)
                tab_panel.setGeometry(x0, y0, wdt, hgt)
                for tab in element["tab"]:
                    widget = tab["widget"]
                    widget.setGeometry(0, 0, wdt, int(hgt - 20 * self.resize_factor - 2))
                    # And resize elements in this tab
                    if tab["element"]:
                        self.resize_elements(tab["element"], widget)
            elif element["style"] == "panel":
                x0, y0, wdt, hgt = self.get_position_from_string(element["position"], parent)
                element["widget"].setGeometry(x0, y0, wdt, hgt)
            elif element["style"] == "olmap":
                x0, y0, wdt, hgt = self.get_position_from_string(element["position"], parent)
                element["widget"].setGeometry(x0, y0, wdt, hgt)
            elif element["style"] == "mapbox":
                x0, y0, wdt, hgt = self.get_position_from_string(element["position"], parent)
#                element["widget"].view.setGeometry(x0, y0, wdt, hgt)
                element["widget"].setGeometry(x0, y0, wdt, hgt)
            elif element["style"] == "webpage":
                x0, y0, wdt, hgt = self.get_position_from_string(element["position"], parent)
                element["widget"].setGeometry(x0, y0, wdt, hgt)

    def get_position_from_string(self, position, parent):

        x0 = position["x"] * self.resize_factor
        y0 = position["y"] * self.resize_factor
        wdt = position["width"] * self.resize_factor
        hgt = position["height"] * self.resize_factor

        if x0>0:
            if wdt>0:
                pass
            else:
                wdt = parent.geometry().width() - x0 + wdt
        else:
            if wdt>0:
                x0 = parent.geometry().width() - wdt
            else:
                x0 = parent.geometry().width() + x0
                wdt = parent.geometry().width() - x0 + wdt

        if y0>0:
            if hgt>0:
                y0 = parent.geometry().height() - (y0 + hgt)
            else:
                y0 = - hgt
                hgt = parent.geometry().height() - position["y"]* self.resize_factor + hgt
        else:
            if hgt>0:
                y0 = parent.geometry().width() - hgt
            else:
                hgt = - y0 - hgt
                y0 = parent.geometry().width() - (y0 + hgt)

        x0 = int(x0)
        y0 = int(y0)
        wdt = int(wdt)
        hgt = int(hgt)

        return x0, y0, wdt, hgt
