import os
from PyQt5.QtWidgets import QPushButton, QLabel, QFileDialog
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class PushSaveFile(QPushButton):

    def __init__(self, element):
        super().__init__(element.text, element.parent.widget)

        self.element = element

        self.setVisible(True)

        self.clicked.connect(self.callback)

        self.set_geometry()
  
    def set(self):
        group  = self.element.variable_group
        name   = self.element.variable
        val    = self.element.getvar(group, name)
        # self.string = str(val)
        # self.setText(str(val))
        # self.setStyleSheet("")

    def callback(self):
        self.okay = True
        group = self.element.variable_group
        name  = self.element.variable
        val   = self.element.getvar(group, name)
        if not val:
            val = os.getcwd()
        fname = QFileDialog.getSaveFileName(self, self.element.title, val, self.element.filter)
        if len(fname[0])>0:
            self.element.setvar(group, name, fname[0])
        else:
            self.okay = False

        try:
            if self.okay and self.element.callback:
                val   = fname[0]
                self.element.callback(val, self)
                # Update GUI
                self.element.window.update()
        except:
            traceback.print_exc()

    def set_geometry(self):
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
