from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
import traceback

class PushButton(QPushButton):

    def __init__(self, element, parent, gui):
        super().__init__(element["text"], parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)

        self.setGeometry(x0, y0, wdt, hgt)

        # if hasattr(element["method"], '__call__'):
        #     # Callback function is already defined as method
        #     self.clicked.connect(element["method"])
        #     self.clicked.connect(gui.update)
        # else:
        if element["module"] :
            if "method" in element:
                if hasattr(element["module"], element["method"]):
                    self.callback = getattr(element["module"] , element["method"])
                    fcn = lambda: self.second_callback()
                    self.clicked.connect(fcn)
                else:
                    print("Error! Method " + element["method"] + " not found!")
            else:
                print("No method found in element. Button will be inactive.")
        self.clicked.connect(gui.update)

        if "icon" in element.keys():
            self.setIcon(QIcon(element["icon"]))
        if "tooltip" in element.keys():
            self.setToolTip(element["tooltip"])


    def set(self):
        pass


    def second_callback(self):
        try:
            self.callback(self)
            # Update GUI
            self.gui.update()
        except:
            traceback.print_exc()
