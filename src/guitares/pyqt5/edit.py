from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class Edit(QLineEdit):

    def __init__(self, element, parent, gui):
        super().__init__("", parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        self.string = None

        if element["type"] == float or element["type"] == int:
            self.setAlignment(QtCore.Qt.AlignRight)
        if not element["enable"]:
            self.setEnabled(False)

        self.setVisible(True)

        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)
        self.setGeometry(x0, y0, wdt, hgt)

        if element["text"]:
            label = QLabel(element["text"], parent)
            fm = label.fontMetrics()
            wlab = fm.size(0, element["text"]).width() + 15
            label.setAlignment(QtCore.Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 6, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")
            if not element["enable"]:
                label.setEnabled(False)
            self.text_widget = label

        fcn1 = lambda: self.first_callback()
        self.editingFinished.connect(fcn1)
        if self.element["module"] and "method" in self.element:
            if hasattr(self.element["module"], self.element["method"]):
                self.callback = getattr(self.element["module"], self.element["method"])
                fcn2 = lambda: self.second_callback()
                self.editingFinished.connect(fcn2)
            else:
               print("Error! Method " + self.element["method"] + " not found!")

    def set(self):
        group  = self.element["variable_group"]
        name   = self.element["variable"]
        val    = self.gui.getvar(group, name)
        self.string = str(val)
        self.setText(str(val))
        self.setStyleSheet("")

    def first_callback(self):
        self.okay = True
        newtext = self.text()
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
            self.setStyleSheet("")
        else:
            self.setStyleSheet("QLineEdit{background-color: red}")

        if self.string == newtext:
            # Nothing changed
            self.okay = False # Not going to run second callback

    def second_callback(self):
        try:
            if self.okay and self.isEnabled():
                group = self.element["variable_group"]
                name  = self.element["variable"]
                val   = self.gui.getvar(group, name)
                self.callback(val, self)
                # Update GUI
                self.gui.update()
        except:
            traceback.print_exc()
