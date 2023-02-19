from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class Text(QLabel):

    def __init__(self, element, parent, gui):
        super().__init__("", parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        # if element["type"] == float or element["type"] == int:
        #     self.setAlignment(QtCore.Qt.AlignRight)
        # if not element["enable"]:
        #     self.setEnabled(False)

        self.setVisible(True)

        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)
        self.setGeometry(x0, y0, wdt, hgt)

    def set(self):
        if "variable" in self.element:
            group = self.element["variable_group"]
            name = self.element["variable"]
            val = self.gui.getvar(group, name)
        else:
            val = self.element["text"]
        self.setText(val)
