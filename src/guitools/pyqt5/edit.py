# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.
#
# This tool is developed for demonstration purposes only.

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore

from .widget_group import WidgetGroup


class Edit(WidgetGroup):
    def __init__(self, element, parent):
        super().__init__(element, parent)

        b = QLineEdit("", self.parent)
        self.widgets.append(b)

        if self.element["type"] == float \
                or self.element["type"] == int:
            b.setAlignment(QtCore.Qt.AlignRight)
        if not element["enable"]:
            b.setEnabled(False)

        x0, y0, wdt, hgt = element["window"].get_position_from_string(self.element["position"], self.parent)
        b.setGeometry(x0, y0, wdt, hgt)
        text = self.element["text"]
        if not text:
            text = ""
        self.label = QLabel(text, self.parent)
        self.widgets.append(self.label)
        fm = self.label.fontMetrics()
        wlab = fm.size(0, text).width() + 15  #15
        self.label.setAlignment(QtCore.Qt.AlignRight)
        self.label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)  # x0 - wlab - 3, y0 + 5, wlab, hgt
        self.label.setStyleSheet("background: transparent; border: none")
        if not element["enable"]:
            self.label.setEnabled(False)

        self.connect(b)

    def set(self):
        if self.check_variables():
            getvar = self.element["getvar"]
            group  = self.element["variable_group"]
            name   = self.element["variable"]
            val    = getvar(group, name)
            self.widgets[0].setText(str(val))
            self.widgets[0].setStyleSheet("")
            self.set_dependencies()

    def connect(self, b):
        fcn1 = lambda: self.first_callback()
        b.editingFinished.connect(fcn1)
        if self.element["module"] and "method" in self.element:
            fcn = getattr(self.element["module"], self.element["method"])
            self.callback = fcn
            fcn2 = lambda: self.second_callback()
            b.editingFinished.connect(fcn2)

    def first_callback(self):
        self.okay = True
        if self.check_variables():
            newtext = self.widgets[0].text()
            if self.element["type"] == int:
                try:
                    newval = int(newtext)
                except:
                    self.okay = False
            elif self.element["type"] == float:
                try:
                    newval = float(newtext)
                except:
                    self.okay = False
            else:
                newval = newtext

            # Do some range checking here ...

            # Update value in variable dict
            if self.okay:
                setvar = self.element["setvar"]
                group  = self.element["variable_group"]
                name   = self.element["variable"]
                setvar(group, name, newval)
                self.widgets[0].setStyleSheet("")
            else:
                self.widgets[0].setStyleSheet("QLineEdit{background-color: red}")

    def second_callback(self):
        if self.okay:
            self.callback()

    def change_background(self, colour):
        self.widgets[0].setStyleSheet(f'QWidget {{background-color: {colour};}}')
        self.connect(self.widgets[0])
