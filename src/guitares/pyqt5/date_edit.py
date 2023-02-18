from PyQt5.QtWidgets import QDateTimeEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class DateEdit(QDateTimeEdit):

    def __init__(self, element, parent, gui):
        super().__init__(parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        self.setCalendarPopup(True)
        self.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)
        self.setGeometry(x0, y0, wdt, hgt)
        if element["text"]:
            label = QLabel("", parent)
            fm = label.fontMetrics()
            wlab = fm.size(0, element["text"]).width() + 15
            label.setAlignment(QtCore.Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")
            self.text_widget = label

        fcn = lambda: self.first_callback()
        self.editingFinished.connect(fcn)
        if self.element["module"] and "method" in self.element:
            self.callback = getattr(self.element["module"], self.element["method"])
            fcn2 = lambda: self.second_callback()
            self.editingFinished.connect(fcn2)


    def set(self):
        group = self.element["variable_group"]
        name  = self.element["variable"]
        val   = self.gui.getvar(group, name)
        dtstr = val.strftime("%Y-%m-%d %H:%M:%S")
        qtDate = QtCore.QDateTime.fromString(dtstr, 'yyyy-MM-dd hh:mm:ss')
        self.setDateTime(qtDate)


    def fist_callback(self):
        newval = self.widgets[0].dateTime().toPyDateTime()
        # Do some range checking here ...
        # Update value in variable dict
        group = self.element["variable_group"]
        name  = self.element["variable"]
        self.gui.setvar(group, name, newval)
        self.okay = True

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
