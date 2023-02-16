from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore

from .widget import Widget

from guitares.gui import get_position

class Edit(Widget):

    def __init__(self, element, parent, gui):
        super().__init__(element, parent, gui)

        if self.element["id"] == "rotation01" or self.element["id"] == "rotation02":
            pass
        b = QLineEdit("", self.parent)
        self.widgets.append(b)

        if self.element["type"] == float \
                or self.element["type"] == int:
            b.setAlignment(QtCore.Qt.AlignRight)
        if not element["enable"]:
            b.setEnabled(False)

        b.setVisible(True)

        x0, y0, wdt, hgt = get_position(element["position"], parent, self.gui.resize_factor)
        b.setGeometry(x0, y0, wdt, hgt)

        if self.element["text"]:
            label = QLabel(self.element["text"], self.parent)
            self.widgets.append(label)
            fm = label.fontMetrics()
            wlab = fm.size(0, self.element["text"]).width() + 15
            label.setAlignment(QtCore.Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")
            if not element["enable"]:
                label.setEnabled(False)

        fcn1 = lambda: self.first_callback()
        b.editingFinished.connect(fcn1)
#        b.textEdited.connect(fcn1)
        if self.element["module"] and "method" in self.element:
            if hasattr(self.element["module"], self.element["method"]):
                self.callback = getattr(self.element["module"], self.element["method"])
                fcn2 = lambda: self.second_callback()
                b.editingFinished.connect(fcn2)
            else:
               print("Error! Method " + self.element["method"] + " not found!")

    def set(self):
        if self.check_variables():
            group  = self.element["variable_group"]
            name   = self.element["variable"]
            val    = self.gui.getvar(group, name)
            self.widgets[0].setText(str(val))
            self.widgets[0].setStyleSheet("")
            self.set_dependencies()

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
                group  = self.element["variable_group"]
                name   = self.element["variable"]
                self.gui.setvar(group, name, newval)
                self.widgets[0].setStyleSheet("")
            else:
                self.widgets[0].setStyleSheet("QLineEdit{background-color: red}")

    def second_callback(self):
        if self.okay and self.widgets[0].isEnabled():
            group = self.element["variable_group"]
            name  = self.element["variable"]
            val   = self.gui.getvar(group, name)
            self.callback(val, self)
            # Update GUI
            self.gui.update()
