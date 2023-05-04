from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
import traceback

class PushButton(QPushButton):

    def __init__(self, element):
        super().__init__("", element.parent.widget)

        self.element = element

        self.clicked.connect(self.callback)

        if element.icon:
            self.setIcon(QIcon(element.icon))

        if element.text:
            if type(element.text) == str:
                txt = element.text
            else:
                txt = self.element.getvar(element.text.variable_group, element.text.variable)    
            self.setText(txt)    

        if self.element.tooltip:
            if type(self.element.tooltip) == str:
                txt = self.element.tooltip
            else:
                txt = self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable)    
            self.setToolTip(txt)

        self.set_geometry()

    def set(self):
        if type(self.element.text) != str:
            self.setText(self.element.getvar(self.element.text.variable_group, self.element.text.variable))   
        if type(self.element.tooltip) != str:
            self.setToolTip(self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable))


    def callback(self):
        try:
            if self.element.callback and self.underMouse():
                self.element.callback(self)
                # Update GUI
                self.element.window.update()
        except:
            traceback.print_exc()

    def set_geometry(self):
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
