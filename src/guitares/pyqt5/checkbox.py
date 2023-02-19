from PyQt5.QtWidgets import QCheckBox
from PyQt5 import QtCore
import traceback

class CheckBox(QCheckBox):

    def __init__(self, element, parent, gui):
        super().__init__("", parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        self.setVisible(True)

        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)
        self.setGeometry(x0, y0, wdt, hgt)

        if element["text"]:
            self.setText(element["text"])

#        fcn1 = lambda: self.first_callback()
        fcn1 = self.first_callback
        self.stateChanged.connect(fcn1)
        if self.element["module"] and "method" in self.element:
            if hasattr(self.element["module"], self.element["method"]):
                self.callback = getattr(self.element["module"], self.element["method"])
#                fcn2 = lambda: self.second_callback()
                fcn2 = self.second_callback
                self.stateChanged.connect(fcn2)
            else:
               print("Error! Method " + self.element["method"] + " not found!")

    def set(self):
        group  = self.element["variable_group"]
        name   = self.element["variable"]
        val    = self.gui.getvar(group, name)
        if val == True:
            self.setChecked = True
        else:
            self.setChecked = False



    def first_callback(self, state):
        group = self.element["variable_group"]
        name = self.element["variable"]
        if state == QtCore.Qt.Checked:
            self.gui.setvar(group, name, True)
        else:
            self.gui.setvar(group, name, False)

    def second_callback(self):
        try:
            if self.isEnabled():
                group = self.element["variable_group"]
                name  = self.element["variable"]
                val   = self.gui.getvar(group, name)
                self.callback(val, self)
                # Update GUI
                self.gui.update()
        except:
            traceback.print_exc()
