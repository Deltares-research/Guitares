from PyQt5.QtWidgets import QButtonGroup, QRadioButton
from PyQt5 import QtCore
import traceback

class RadioButtonGroup(QButtonGroup):

    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element

        x0, y0, wdt, hgt = element.get_position()

        # Lower y of top button
        yll = y0 + hgt - int(len(element.option_value.list) * 20 * element.resize_factor)
        for i in range(len(element.option_value.list)):
            d = QRadioButton(element.option_string.list[i], element.parent.widget)
            d.setGeometry(x0, int(yll + i*20*element.resize_factor), wdt, int(20 * element.resize_factor))
            d.setVisible(True)
            d.id = i
            self.addButton(d)
            self.buttonClicked.connect(self.callback)

    def set(self):
        group  = self.element.variable_group
        name   = self.element.variable
        val    = self.element.getvar(group, name)
        values = self.element.option_value.list
        indx   = values.index(val)
        self.buttons()[indx].setChecked(True)

    def callback(self, button):
        group = self.element.variable_group
        name = self.element.variable
        values = self.element.option_value.list
        self.element.setvar(group, name, values[button.id])

        try:
            if self.element.callback:
                self.element.callback(values[button.id], self)
                # Update GUI
                self.element.window.update()
        except:
            traceback.print_exc()
