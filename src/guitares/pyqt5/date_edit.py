from PyQt5.QtWidgets import QDateTimeEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore

from .widget import Widget
from guitares.gui import get_position

class DateEdit(Widget):

    def __init__(self, element, parent, gui):
        super().__init__(element, parent, gui)

        b = QDateTimeEdit(parent)
        self.widgets.append(b)

        b.setCalendarPopup(True)
        b.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        x0, y0, wdt, hgt = get_position(element["position"], parent, self.gui.resize_factor)
        b.setGeometry(x0, y0, wdt, hgt)
        if element["text"]:
            label = QLabel(self.element["text"], self.parent)
            self.widgets.append(label)
            fm = label.fontMetrics()
            wlab = fm.size(0, element["text"]).width() + 15
            label.setAlignment(QtCore.Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")

        fcn = lambda: self.callback()
        b.editingFinished.connect(fcn)
        if self.element["module"] and "method" in self.element:
            self.callback = getattr(self.element["module"], self.element["method"])
            fcn2 = lambda: self.second_callback()
            b.editingFinished.connect(fcn2)


    def set(self):
        if self.check_variables():
            group = self.element["variable_group"]
            name  = self.element["variable"]
            val   = self.gui.getvar(group, name)
            dtstr = val.strftime("%Y-%m-%d %H:%M:%S")
            qtDate = QtCore.QDateTime.fromString(dtstr, 'yyyy-MM-dd hh:mm:ss')
            self.widgets[0].setDateTime(qtDate)
            self.set_dependencies()


    def fist_callback(self):
        if self.check_variables():

            newval = self.widgets[0].dateTime().toPyDateTime()

            # Do some range checking here ...

            # Update value in variable dict
            group = self.element["variable_group"]
            name  = self.element["variable"]
            self.gui.setvar(group, name, newval)

    def second_callback(self):
        if self.okay and self.widgets[0].isEnabled():
            group = self.element["variable_group"]
            name  = self.element["variable"]
            val   = self.gui.getvar(group, name)
            self.callback(val, self)
            # Update GUI
            self.gui.update()
