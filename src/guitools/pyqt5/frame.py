import importlib
from PyQt5.QtWidgets import QWidget, QFrame, QLabel
from PyQt5 import QtCore

from guitools.gui import get_position_from_string

class Frame:

    def __init__(self, element, parent):

        # Add tab panel
        frame = QFrame(parent)
        
        element["widget"] = frame
        element["parent"] = parent

        x0, y0, wdt, hgt = get_position_from_string(element["position"], parent, element["window"].resize_factor)

        frame.setGeometry(x0, y0, wdt, hgt)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setLineWidth(2)

        if element["title"]:
            label = QLabel(element["title"], frame)
            fm = label.fontMetrics()
            wlab = fm.size(0, element["title"]).width() + 15
            label.setAlignment(QtCore.Qt.AlignLeft)
            #                    label.setGeometry(x0 + 10, y0 - 5, wlab, 20)
            label.setGeometry(10, -2, wlab, 16)
