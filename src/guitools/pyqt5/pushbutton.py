from PyQt5.QtWidgets import QPushButton
#from PyQt5.QtWidgets import QLabel
#from PyQt5 import QtCore

from pyqt5_widget_group import PyQt5WidgetGroup

from gui import getvar

class PyQt5PushButton(PyQt5WidgetGroup):

    def __init__(self, element, parent):
        super().__init__(element, parent)

        b = QPushButton(element["text"], parent)
        self.widgets.append(b)

        x0, y0, wdt, hgt = element["window"].get_position_from_string(self.element["position"], self.parent)
        b.setGeometry(x0, y0, wdt, hgt)
        if self.module:
            if "method" in self.element:
                fcn = getattr(self.module, self.element["method"])
                b.clicked.connect(fcn)
            else:
                print("No method found in element !")

    def set(self):
        self.set_dependencies()

    def callback(self):
        # Callback already set
        pass
