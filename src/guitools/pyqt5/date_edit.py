from PyQt5.QtWidgets import QDateTimeEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore

from .widget_group import WidgetGroup

class DateEdit(WidgetGroup):

    def __init__(self, element, parent):
        super().__init__(element, parent)

        b = QDateTimeEdit(parent)
        self.widgets.append(b)

        b.setCalendarPopup(True)
        b.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        x0, y0, wdt, hgt = element["window"].get_position_from_string(self.element["position"], self.parent)
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
            fcn = getattr(self.element["module"], self.element["method"])
            self.callback = fcn
            fcn2 = lambda: self.second_callback()
            b.editingFinished.connect(fcn2)



    def set(self):
        if self.check_variables():
            getvar = self.element["getvar"]
            group = self.element["variable_group"]
            name  = self.element["variable"]
            val   = getvar(group, name)
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
            setvar(group, name, newval)

    def second_callback(self):
        if self.okay:
            self.callback()
