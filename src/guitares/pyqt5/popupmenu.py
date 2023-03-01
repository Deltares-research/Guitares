from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class PopupMenu(QComboBox):
    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element

        if element.option_string.variable:
            group = element.option_string.variable_group
            name  = element.option_string.variable
            v     = element.getvar(group, name)
            for txt in v:
                self.addItem(txt)
        else:
            for txt in element.option_string.list:
                self.addItem(txt)

        # Adjust list value types
        if element.option_value:
            if not type(element.option_value.variable):
                for i, val in enumerate(element.option_value.list):
                    if element.type == float:
                        element.option_value[i] = float(val)
                    elif element.type == int:
                        element.option_value[i] = int(val)

        if element.text:
            label = QLabel(element.text, element.parent.widget)
            label.setStyleSheet("background: transparent; border: none")
            self.text_widget = label

        self.currentIndexChanged.connect(self.callback)

        self.set_geometry()

    def set(self):

        if self.element.select == "item":
            if self.element.option_value:
                if self.element.option_value.variable:
                    name  = self.element.option_value.variable
                    group = self.element.option_value.variable_group
                    self.element.option_value.list = self.element.getvar(group, name)

            val = self.element.getvar(self.element.variable_group, self.element.variable)
            if val:
                if self.element.option_value:
                    index = self.element.option_value.list.index(val)
                    self.setCurrentIndex(index)
        else:
            name = self.element.option_value.variable
            group = self.element.option_value.variable_group
            index = self.element.getvar(group, name)
            self.setCurrentIndex(index)

    def callback(self):
        i = self.currentIndex()
        newval = i
        if not self.element.option_value.variable:
            newval = self.element.option_value.list[i]
        name  = self.element.variable
        group = self.element.variable_group
        self.element.setvar(group, name, newval)

        try:
            if self.isEnabled() and self.element.callback:
                self.element.callback(newval, self)
                # Update GUI
            self.element.window.update()
        except:
            traceback.print_exc()

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        if self.element.text:
            label = self.text_widget
            fm = label.fontMetrics()
            wlab = int(fm.size(0, self.element.text).width())
            if self.element.text_position == "above-center" or self.element.text_position == "above":
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setGeometry(x0, int(y0 - 20 * resize_factor), wdt, int(20 * resize_factor))
            elif self.element.text_position == "above-left":
                label.setAlignment(QtCore.Qt.AlignLeft)
                label.setGeometry(x0, int(y0 - 20 * resize_factor), wlab, int(20 * resize_factor))
            else:
                # Assuming left
                label.setAlignment(QtCore.Qt.AlignRight)
                label.setGeometry(int(x0 - wlab - 3 * resize_factor),
                                  int(y0 + 5 * self.element.gui.resize_factor),
                                  wlab,
                                  int(20 * resize_factor))
