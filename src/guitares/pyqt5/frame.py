from PyQt5.QtWidgets import QWidget, QFrame, QLabel
from PyQt5 import QtCore

class Frame(QFrame):
    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element

        x0, y0, wdt, hgt = element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)

        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(2)

        if element.text:
            label = QLabel(element.text, element.parent.widget)
            fm = label.fontMetrics()
            wlab = fm.size(0, element.text).width()
            label.setGeometry(x0 + 10, y0 - 9, wlab, 16)
            label.setAlignment(QtCore.Qt.AlignTop)
            element.text_width = wlab # Used for resizing
            self.text_widget = label

    def set(self):
        pass
