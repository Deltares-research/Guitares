from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore

from .widget import Widget

from guitares.gui import get_position

class PopupMenu(Widget):

    def __init__(self, element, parent, gui):
        super().__init__(element, parent, gui)

        b = QComboBox(parent)
        self.widgets.append(b)

        if "option_string" in self.element:
            if type(self.element["option_string"]) == dict:
                group = self.element["option_string"]["variable_group"]
                name  = self.element["option_string"]["variable"]
                v     = self.gui.getvar(group, name)
                for txt in v:
                    b.addItem(txt)
            else:
                for txt in self.element["option_string"]:
                    b.addItem(txt)

        # Adjust list value types
        if self.element["option_value"]:
            if not type(self.element["option_value"]) == dict:
                for i, val in enumerate(self.element["option_value"]):
                    if "type" not in self.element:
                        print(self.element["variable"])
                        pass
                    if self.element["type"] == float:
                        self.element["option_value"][i] = float(val)
                    elif self.element["type"] == int:
                        self.element["option_value"][i] = int(val)
            # else:
            #     group = self.element["option_value"]["variable_group"]
            #     name  = self.element["option_value"]["variable"]
            #     v = variables[self.element["option_value"]]

        x0, y0, wdt, hgt = get_position(element["position"], parent, self.gui.resize_factor)

        b.setGeometry(x0, y0, wdt, hgt)
        if element["text"]:
            label = QLabel(self.element["text"], self.parent)
            self.widgets.append(label)
            fm = label.fontMetrics()
            wlab = fm.size(0, self.element["text"]).width() + 15
            label.setAlignment(QtCore.Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")

        fcn = lambda: self.first_callback()
        b.currentIndexChanged.connect(fcn)
        if self.element["module"] and "method" in self.element:
            self.callback = getattr(self.element["module"], self.element["method"])
            fcn2 = lambda: self.second_callback()
            b.currentIndexChanged.connect(fcn2)

    def set(self):
        if self.check_variables():
            if self.element["option_value"]:
                if type(self.element["option_value"]) == dict:
                    name  = self.element["option_value"]["variable"]
                    group = self.element["option_value"]["variable_group"]
                    self.element["option_value"] = self.gui.getvar(group, name)

            val = self.gui.getvar(self.element["variable_group"], self.element["variable"])
            if val:
                if self.element["option_value"]:
                    index = self.element["option_value"].index(val)
                    self.widgets[0].setCurrentIndex(index)
                self.set_dependencies()

    def first_callback(self):
        if self.check_variables():
            i = self.widgets[0].currentIndex()
            newval = i
            if self.element["option_value"]:
                newval = self.element["option_value"][i]
            name  = self.element["variable"]
            group = self.element["variable_group"]
            self.gui.setvar(group, name, newval)

    def second_callback(self):
        if self.okay and self.widgets[0].isEnabled():
            group = self.element["variable_group"]
            name  = self.element["variable"]
            val   = self.gui.getvar(group, name)
            self.callback(val, self)
            # Update GUI
            self.gui.update()
