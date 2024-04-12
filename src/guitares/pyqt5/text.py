from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import traceback

class Text(QLabel):

    def __init__(self, element):
        super().__init__("", element.parent.widget)

        self.element = element

        self.setVisible(True)

        self.set_geometry()
        
        if self.element.text_position:
            self.setAlignment(Text.convert_to_qt_alignment(self.element.text_position))

    def set(self):
        if self.element.variable:
            group = self.element.variable_group
            name = self.element.variable
            val = self.element.getvar(group, name)
        else:
            val = self.element.text
        self.setText(val)

    def set_geometry(self):
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)

    def convert_to_qt_alignment(alignment_string):
        alignment_mapping = {
            'left': Qt.AlignLeft | Qt.AlignVCenter,	# This is also the default for when nothing is specified
            'right': Qt.AlignRight | Qt.AlignVCenter,
            'top': Qt.AlignTop | Qt.AlignHCenter,
            'bottom': Qt.AlignBottom | Qt.AlignHCenter,
            'top-left': Qt.AlignTop | Qt.AlignLeft,
            'top-right': Qt.AlignTop | Qt.AlignRight,
            'bottom-left': Qt.AlignBottom | Qt.AlignLeft,
            'bottom-right': Qt.AlignBottom | Qt.AlignRight,
            'center': Qt.AlignCenter
        }

        return alignment_mapping.get(alignment_string, Qt.AlignLeft | Qt.AlignVCenter)