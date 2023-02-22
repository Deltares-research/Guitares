from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
import traceback

class PushButton(QPushButton):

    def __init__(self, element):
        super().__init__(element.text, element.parent.widget)

        self.element = element

        x0, y0, wdt, hgt = element.get_position()

        self.setGeometry(x0, y0, wdt, hgt)

        self.clicked.connect(self.callback)

        if element.icon:
            self.setIcon(QIcon(element.icon))
        if element.tooltip:
            self.setToolTip(element.tooltip)

    def set(self):
        pass


    def callback(self):
        try:
            if self.element.callback:
                self.element.callback(self)
                # Update GUI
                self.element.window.update()
        except:
            traceback.print_exc()
