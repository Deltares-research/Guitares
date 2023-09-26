from PyQt5.QtWidgets import QDateTimeEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback
import datetime

class DateEdit(QDateTimeEdit):

    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element

        self.setCalendarPopup(True)
        self.setDisplayFormat("yyyy-MM-dd hh:mm:ss")

        if element.text:
            if type(element.text) == str:
                txt = element.text
            else:
                txt = self.element.getvar(element.text.variable_group, element.text.variable)    
            label = QLabel(txt, element.parent.widget)
            label.setStyleSheet("background: transparent; border: none")
            if not element.enable:
                label.setEnabled(False)
            self.text_widget = label
            label.setVisible(True)

        if self.element.tooltip:
            if type(self.element.tooltip) == str:
                txt = self.element.tooltip
            else:
                txt = self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable)    
            self.setToolTip(txt)

        self.editingFinished.connect(self.callback)

        self.set_geometry()

    def set(self):
        group = self.element.variable_group
        name  = self.element.variable
        val   = self.element.getvar(group, name)
        if type(val) == str:
            # Value is a string. Need to convert to datetime using Python datetime.
            val = datetime.datetime.strptime(val, "%Y%m%d %H%M%S")
        dtstr = val.strftime("%Y-%m-%d %H:%M:%S")
        qtDate = QtCore.QDateTime.fromString(dtstr, 'yyyy-MM-dd hh:mm:ss')
        self.setDateTime(qtDate)

        if type(self.element.text) != str:
            txt = self.element.getvar(self.element.text.variable_group, self.element.text.variable)
            self.text_widget.setText(txt)

        if type(self.element.tooltip) != str:
            txt = self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable)    
            self.setToolTip(txt)


    def callback(self):
        group = self.element.variable_group
        name  = self.element.variable
        newval = self.dateTime().toPyDateTime()
        if type(self.element.getvar(group, name)) == str:
            # Expected value is a string. Need to convert to newval to string.
            newval = newval.strftime("%Y%m%d %H%M%S")
        # Do some range checking here ...
        # Update value in variable dict
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
