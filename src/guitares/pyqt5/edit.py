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

        if element.text:
            label = QLabel(element.text, element.parent.widget)
            label.setStyleSheet("background: transparent; border: none")
            if not element.enable:
                label.setEnabled(False)
            self.text_widget = label
            label.setVisible(True)

        self.editingFinished.connect(self.callback)

        self.set_geometry()

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
