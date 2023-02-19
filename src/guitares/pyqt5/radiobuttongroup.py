from PyQt5.QtWidgets import QButtonGroup, QRadioButton
from PyQt5 import QtCore
import traceback

class RadioButtonGroup(QButtonGroup):

    def __init__(self, element, parent, gui):
        super().__init__(parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)

        fcn1 = self.first_callback
        if self.element["module"] and "method" in self.element:
            if hasattr(self.element["module"], self.element["method"]):
                self.callback = getattr(self.element["module"], self.element["method"])
                fcn2 = self.second_callback

        # Lower y of top button
        yll = y0 + hgt - int(len(element["option_value"]) * 20 * gui.resize_factor)
        for i in range(len(element["option_value"])):
            d = QRadioButton(element["option_string"][i], parent)
            d.setGeometry(x0, int(yll + i*20*gui.resize_factor), wdt, int(20 * gui.resize_factor))
            d.setVisible(True)
            d.id = i
            self.addButton(d)
            self.buttonClicked.connect(fcn1)
            self.buttonClicked.connect(fcn2)

    def set(self):
        group  = self.element["variable_group"]
        name   = self.element["variable"]
        val    = self.gui.getvar(group, name)
        values = self.element["option_value"]
        indx   = values.index(val)
        self.buttons()[indx].setChecked(True)

    def first_callback(self, button):
        group = self.element["variable_group"]
        name = self.element["variable"]
        values = self.element["option_value"]
        self.gui.setvar(group, name, values[button.id])

    def second_callback(self, button):
        try:
            group = self.element["variable_group"]
            name  = self.element["variable"]
            values = self.element["option_value"]
            self.callback(values[button.id], self)
            # Update GUI
            self.gui.update()
        except:
            traceback.print_exc()
