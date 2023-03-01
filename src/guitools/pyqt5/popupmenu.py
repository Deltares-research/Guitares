# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore

from .widget_group import WidgetGroup

#from gui import getvar, setvar

class PopupMenu(WidgetGroup):

    def __init__(self, element, parent):
        super().__init__(element, parent)

        b = QComboBox(parent)
        self.widgets.append(b)

        if "option_string" in self.element:
            if type(self.element["option_string"]) == dict:
                getvar = self.element["getvar"]
                group = self.element["option_string"]["variable_group"]
                name  = self.element["option_string"]["variable"]
                v     = getvar(group, name)
                for txt in v:
                    b.addItem(txt)
            else:
                for txt in self.element["option_string"]:
                    b.addItem(txt)

        # Adjust list value types
        if self.element["option_value"]:
            if not type(self.element["option_value"]) == dict:
                for i, val in enumerate(self.element["option_value"]):
                    if self.element["type"] == float:
                        self.element["option_value"][i] = float(val)
                    elif self.element["type"] == int:
                        self.element["option_value"][i] = int(val)
            # else:
            #     group = self.element["option_value"]["variable_group"]
            #     name  = self.element["option_value"]["variable"]
            #     v = variables[self.element["option_value"]]

        x0, y0, wdt, hgt = element["window"].get_position_from_string(self.element["position"], self.parent)
        b.setGeometry(x0, y0, wdt, hgt)
        if element["text"]:
            label = QLabel(self.element["text"], self.parent)
            self.widgets.append(label)
            fm = label.fontMetrics()
            wlab = fm.size(0, self.element["text"]).width() + 15
            label.setAlignment(QtCore.Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")

        fcn = lambda: self.callback()
        b.currentIndexChanged.connect(fcn)
        if self.element["module"] and "method" in self.element:
            fcn = getattr(self.element["module"], self.element["method"])
            b.currentIndexChanged.connect(fcn)

    def set(self):
        if self.check_variables():
            if self.element["option_value"]:
                if type(self.element["option_value"]) == dict:
                    getvar = self.element["getvar"]
                    name  = self.element["option_value"]["variable"]
                    group = self.element["option_value"]["variable_group"]
                    self.element["option_value"] = getvar(group, name)

            getvar = self.element["getvar"]
            val = getvar(self.element["variable_group"], self.element["variable"])
            if self.element["option_value"]:
                index = self.element["option_value"].index(val)
                self.widgets[0].setCurrentIndex(index)
            self.set_dependencies()

    def callback(self):
        if self.check_variables():
            i = self.widgets[0].currentIndex()
            newval = i
            if self.element["option_value"]:
                newval = self.element["option_value"][i]
            setvar = self.element["setvar"]
            name  = self.element["variable"]
            group = self.element["variable_group"]
            setvar(group, name, newval)
