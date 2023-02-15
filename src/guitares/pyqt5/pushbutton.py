from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
#from PyQt5.QtWidgets import QLabel
#from PyQt5 import QtCore

from .widget import Widget
from guitares.gui import get_position

class PushButton(Widget):

    def __init__(self, element, parent, gui):
        super().__init__(element, parent, gui)

        b = QPushButton(element["text"], parent)
        self.widgets.append(b)

        x0, y0, wdt, hgt = get_position(element["position"], parent, self.gui.resize_factor)

        b.setGeometry(x0, y0, wdt, hgt)

        if hasattr(element["method"], '__call__'):
            # Callback function is already defined as method
            b.clicked.connect(element["method"])
            b.clicked.connect(self.gui.update)
        else:
            if element["module"] :
                if "method" in element:
                    try:
                        self.callback = getattr(element["module"] , element["method"])
                        fcn = lambda: self.second_callback()
                        b.clicked.connect(fcn)
                    except:
                        print("ERROR! Method " + element["method"] + " not found!")
                else:
                    print("No method found in element !")
        b.clicked.connect(self.gui.update)

        if "icon" in element.keys():
            b.setIcon(QIcon(element["icon"]))
        if "tooltip" in element.keys():
            b.setToolTip(element["tooltip"])


    def set(self):
        self.set_dependencies()

    def second_callback(self):
        self.callback(self)
        # Update GUI
        self.gui.update()
