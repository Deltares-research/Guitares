from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
#from PyQt5.QtWidgets import QLabel
#from PyQt5 import QtCore

from .widget_group import WidgetGroup
from guitools.gui import get_position_from_string

class PushButton(WidgetGroup):

    def __init__(self, element, parent):
        super().__init__(element, parent)

        b = QPushButton(element["text"], parent)
        self.widgets.append(b)

        x0, y0, wdt, hgt = get_position_from_string(element["position"], parent, element["window"].resize_factor)

        b.setGeometry(x0, y0, wdt, hgt)

        if hasattr(element["method"], '__call__'):
            # Callback function is already defined as method
            b.clicked.connect(element["method"])
        else:
            if element["module"] :
                if "method" in element:
                    try:
                        fcn = getattr(element["module"] , element["method"])
                        b.clicked.connect(fcn)
                    except:
                        print("ERROR! Method " + element["method"] + " not found!")
                else:
                    print("No method found in element !")
        if "icon" in element.keys():
            b.setIcon(QIcon(element["icon"]))
        if "tooltip" in element.keys():
            b.setToolTip(element["tooltip"])


    def set(self):
        self.set_dependencies()

    def callback(self):
        # Callback already set
        pass
