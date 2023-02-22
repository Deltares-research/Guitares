from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class Edit(QLineEdit):

    def __init__(self, element):
        super().__init__("", element.parent.widget)

        self.element = element

        self.string = None

        if element.type == float or element.type == int:
            self.setAlignment(QtCore.Qt.AlignRight)
        if not element.enable:
            self.setEnabled(False)

        self.setVisible(True)

        x0, y0, wdt, hgt = element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)

        if element.text:
            label = QLabel(element.text, element.parent.widget)
            fm = label.fontMetrics()
            wlab = fm.size(0, element.text).width() + 15
            label.setAlignment(QtCore.Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 6, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")
            if not element.enable:
                label.setEnabled(False)
            self.text_widget = label
            label.setVisible(True)

        self.editingFinished.connect(self.callback)

    def set(self):
        group  = self.element.variable_group
        name   = self.element.variable
        val    = self.element.getvar(group, name)
        self.string = str(val)
        self.setText(str(val))
        self.setStyleSheet("")

    def callback(self):
        self.okay = True
        newtext = self.text()
        if self.element.type == int:
            try:
                newval = int(newtext)
            except:
                self.okay = False
        elif self.element.type == float:
            try:
                newval = float(newtext)
            except:
                self.okay = False
        else:
            newval = newtext

        # Do some range checking here ...

        # Update value in variable dict
        if self.okay:
            group = self.element.variable_group
            name = self.element.variable
            self.element.setvar(group, name, newval)
            self.setStyleSheet("")
        else:
            self.setStyleSheet("QLineEdit{background-color: red}")

        if self.string == newtext:
            # Nothing changed
            self.okay = False # Not going to run second callback

        try:
            if self.okay and self.isEnabled() and self.element.callback:
                group = self.element.variable_group
                name = self.element.variable
                val   = newval
                self.element.callback(val, self)
                # Update GUI
                self.element.window.update()
        except:
            traceback.print_exc()
