import os
from PyQt5.QtWidgets import QPushButton, QLabel, QFileDialog
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class PushSaveFile(QPushButton):

    def __init__(self, element):
        super().__init__("", element.parent.widget)

        self.element = element

        if element.text:
            if type(element.text) == str:
                txt = element.text
            else:
                txt = self.element.getvar(element.text.variable_group, element.text.variable)    
            self.setText(txt)    

        if self.element.tooltip:
            if type(self.element.tooltip) == str:
                txt = self.element.tooltip
            else:
                txt = self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable)    
            self.setToolTip(txt)

        self.setVisible(True)

        self.clicked.connect(self.callback)

        self.set_geometry()
  
    def set(self):
        if type(self.element.text) != str:
            self.setText(self.element.getvar(self.element.text.variable_group, self.element.text.variable))   
        if type(self.element.tooltip) != str:
            self.setToolTip(self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable))
        # group  = self.element.variable_group
        # name   = self.element.variable
        # val    = self.element.getvar(group, name)
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
