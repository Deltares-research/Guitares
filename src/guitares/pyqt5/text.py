from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class Text(QLabel):

    def __init__(self, element):
        super().__init__("", element.parent.widget)

        self.element = element

        self.setVisible(True)

        x0, y0, wdt, hgt = element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)

    def set(self):
        if self.element.variable:
            group = self.element.variable_group
            name = self.element.variable
            val = self.element.getvar(group, name)
        else:
            val = self.element.text
        self.setText(val)
