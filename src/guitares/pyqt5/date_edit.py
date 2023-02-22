from PyQt5.QtWidgets import QDateTimeEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class DateEdit(QDateTimeEdit):

    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element

        self.setCalendarPopup(True)
        self.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        x0, y0, wdt, hgt = element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        if element.text:
            label = QLabel("", element.parent.widget)
            fm = label.fontMetrics()
            wlab = fm.size(0, element.text).width() + 15
            label.setAlignment(QtCore.Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")
            self.text_widget = label

        self.editingFinished.connect(self.callback)

    def set(self):
        group = self.element.variable_group
        name  = self.element.variable
        val   = self.element.getvar(group, name)
        dtstr = val.strftime("%Y-%m-%d %H:%M:%S")
        qtDate = QtCore.QDateTime.fromString(dtstr, 'yyyy-MM-dd hh:mm:ss')
        self.setDateTime(qtDate)


    def callback(self):
        newval = self.dateTime().toPyDateTime()
        # Do some range checking here ...
        # Update value in variable dict
        group = self.element.variable_group
        name  = self.element.variable
        self.element.setvar(group, name, newval)
        self.okay = True
        try:
            if self.okay and self.isEnabled() and self.element.callback:
                val   = newval
                self.element.callback(val, self)
                # Update GUI
                self.element.window.update()
        except:
            traceback.print_exc()
