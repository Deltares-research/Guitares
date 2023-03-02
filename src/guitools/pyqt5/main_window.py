# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.
#
# This tool is developed for demonstration purposes only.

from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QVBoxLayout
from PyQt5 import QtGui, QtCore


class MainWindow(QMainWindow):
    def __init__(self, gui):
        super().__init__()

        self.gui = gui

        screen = QApplication.primaryScreen()
        if screen.size().width() > 2500:
            self.resize_factor = 1.4
        elif screen.size().width() > 1200:
            self.resize_factor = 1.4
        else:
            self.resize_factor = 1.0

        self.set_window()
        self.add_toolbar()
        
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.central_widget = widget

    def resizeEvent(self, event):
        self.resize_elements(self.gui.config["element"], self.central_widget)

    def closeEvent(self,event):
        QApplication.quit()        

    def set_window(self):
        # Window size
        self.setWindowTitle(self.gui.config["window"]["title"])
        self.window_width = int(self.gui.config["window"]["width"]*self.resize_factor)
        self.window_height = int(self.gui.config["window"]["height"]*self.resize_factor)
        self.setMinimumSize(self.window_width, self.window_height)

        screen = QApplication.primaryScreen()

        self.setGeometry(int(0.5*(screen.size().width() - self.window_width)),
                         int(0.5*(screen.size().height() - self.window_height)),
                         self.window_width,
                         self.window_height)

        if self.gui.config["window"]["icon"]:
            self.setWindowIcon(QtGui.QIcon(self.gui.config["window"]["icon"]))

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

                if element['label'] and element["title_width"]:
                    # Also change title widget
                    element["label"].setGeometry(x0 + 10, y0 - 9, element["title_width"], 16)
                    element["label"].setAlignment(QtCore.Qt.AlignTop)
                    element["label"].adjustSize()
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
