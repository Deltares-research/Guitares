from PyQt5.QtWidgets import QButtonGroup, QRadioButton
from PyQt5 import QtCore
import traceback

class RadioButtonGroup(QButtonGroup):

    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element

        for i in range(len(element.option_value.list)):
            d = QRadioButton(element.option_string.list[i], element.parent.widget)
            d.setVisible(True)
            d.id = i
            self.addButton(d)
            self.buttonClicked.connect(self.callback)

        self.set_geometry()

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

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        nbuttons = len(self.element.option_value.list)
        # Lower y of top button
        yll = y0 + hgt - int(nbuttons * 20 * resize_factor)
        for i in range(nbuttons):
            self.buttons()[i].setGeometry(x0,
                                          int(yll + i * 20 * resize_factor),
                                          wdt,
                                          int(20 * resize_factor))

    def set_enabled(self, true_or_false):
        nbuttons = len(self.element.option_value.list)
        for i in range(nbuttons):
            self.buttons()[i].setEnabled(true_or_false)

    def set_visible(self, true_or_false):
        nbuttons = len(self.element.option_value.list)
        for i in range(nbuttons):
            self.buttons()[i].setVisible(true_or_false)
