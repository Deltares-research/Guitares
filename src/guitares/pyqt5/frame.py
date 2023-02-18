from PyQt5.QtWidgets import QWidget, QFrame, QLabel
from PyQt5 import QtCore

class Frame(QFrame):
    def __init__(self, element, parent, gui):
        super().__init__(parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)
        self.setGeometry(x0, y0, wdt, hgt)

        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(2)

        if element["text"]:
            label = QLabel(element["text"], parent)
            fm = label.fontMetrics()
            wlab = fm.size(0, element["text"]).width()
            label.setGeometry(x0 + 10, y0 - 9, wlab, 16)
            label.setAlignment(QtCore.Qt.AlignTop)
            element["text_width"] = wlab # Used for resizing
            self.text_widget = label

        self.setVisible(True)

    def set(self):
        pass
