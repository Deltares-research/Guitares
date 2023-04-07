from PyQt5.QtWidgets import QCheckBox
from PyQt5 import QtCore
import traceback

class CheckBox(QCheckBox):

    def __init__(self, element):
        super().__init__("", element.parent.widget)

        self.element = element

        self.setVisible(True)

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

        self.stateChanged.connect(self.callback)

        self.set_geometry()

    def set(self):
        group  = self.element.variable_group
        name   = self.element.variable
        val    = self.element.getvar(group, name)
        if val == True:
            self.setChecked(True)
        else:
            self.setChecked(False)
            
        if type(self.element.text) != str:
            self.setText(self.element.getvar(self.element.text.variable_group, self.element.text.variable))   
        if type(self.element.tooltip) != str:
            self.setToolTip(self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable))

    def callback(self, state):
        group = self.element.variable_group
        name = self.element.variable
        if state == QtCore.Qt.Checked:
            val = True
        else:
            val = False
        self.element.setvar(group, name, True)
        try:
            if self.isEnabled() and self.element.callback:
                self.element.callback(val, self)
                # Update GUI
                self.element.window.update()
        except:
            traceback.print_exc()

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)

