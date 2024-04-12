from PyQt5.QtWidgets import QCheckBox
from PyQt5 import QtCore
import traceback

class CheckBox(QCheckBox):

    def __init__(self, element):
        super().__init__("", element.parent.widget)

        self.element = element

        self.setVisible(True)

        if element.text:
            if isinstance(element.text, str):
                txt = element.text
            else:
                txt = self.element.getvar(element.text.variable_group, element.text.variable)    
            self.setText(txt)    

        if self.element.tooltip:
            if isinstance(self.element.tooltip, str):
                txt = self.element.tooltip
            else:
                txt = self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable)    
            self.setToolTip(txt)

        # self.stateChanged.connect(self.callback)
        self.clicked.connect(self.callback)

        self.set_geometry()

    def set(self):
        group  = self.element.variable_group
        name   = self.element.variable
        val    = self.element.getvar(group, name)
        if val is True:
            self.setChecked(True)
        else:
            self.setChecked(False)
            
        if not isinstance(self.element.text, str):
            self.setText(self.element.getvar(self.element.text.variable_group, self.element.text.variable))   
        if not isinstance(self.element.tooltip, str):
            self.setToolTip(self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable))

    def callback(self, state):
        group = self.element.variable_group
        name = self.element.variable
        val = state
        self.element.setvar(group, name, val)
        try:
            if self.isEnabled() and self.element.callback:
                self.element.callback(val, self)
            # Update GUI
            self.element.window.update()
        except Exception as e:
            print("Error in CheckBox callback")
            print(e)

    def set_geometry(self):
        if self.element.id=="sbg":
            pass
        x0, y0, wdt, hgt = self.element.get_position()
        # Get the width of the text in pixels and add 25 pixels
        txt = self.text()
        wdt = self.fontMetrics().boundingRect(txt).width() + 25
        self.setGeometry(x0, y0, wdt, hgt)

