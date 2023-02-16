from PyQt5.QtWidgets import QWidget, QFrame, QLabel
from PyQt5 import QtCore

from guitares.gui import get_position
from .widget import Widget

class Frame(Widget):
    def __init__(self, element, parent, gui):
        super().__init__(element, parent, gui)

        # Add tab panel
        frame = QFrame(parent)
        self.widgets.append(frame)

        x0, y0, wdt, hgt = get_position(element["position"], parent, self.gui.resize_factor)
        frame.setGeometry(x0, y0, wdt, hgt)

        frame.setFrameShape(QFrame.StyledPanel)
        frame.setLineWidth(2)

        # if element["title"]:
        #     label = QLabel(element["title"], frame)
        #     fm = label.fontMetrics()
        #     wlab = fm.size(0, element["title"]).width() + 15
        #     label.setAlignment(QtCore.Qt.AlignLeft)
        #     #                    label.setGeometry(x0 + 10, y0 - 5, wlab, 20)
        #     label.setGeometry(10, -2, wlab, 16)

        if element["title"]:
            label = QLabel(element["title"], parent)
            fm = label.fontMetrics()
            wlab = fm.size(0, element["title"]).width()
            label.setAlignment(QtCore.Qt.AlignLeft)
            #                    label.setGeometry(x0 + 10, y0 - 5, wlab, 20)
            label.setGeometry(x0 + 10, y0, wlab, 16)
            element["title_width"] = wlab
            self.widgets.append(label)


        frame.setVisible(True)
