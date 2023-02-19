import os
from PyQt5.QtWidgets import QPushButton, QLabel, QFileDialog
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class PushOpenFile(QPushButton):

    def __init__(self, element, parent, gui):
        super().__init__(element["text"], parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        self.setVisible(True)

        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)
        self.setGeometry(x0, y0, wdt, hgt)

        # if element["text"]:
        #     label = QLabel(element["text"], parent)
        #     fm = label.fontMetrics()
        #     wlab = fm.size(0, element["text"]).width() + 15
        #     label.setAlignment(QtCore.Qt.AlignRight)
        #     label.setGeometry(x0 - wlab - 3, y0 + 6, wlab, hgt)
        #     label.setStyleSheet("background: transparent; border: none")
        #     if not element["enable"]:
        #         label.setEnabled(False)
        #     self.text_widget = label
        #     label.setVisible(True)

        fcn1 = lambda: self.first_callback()
        self.clicked.connect(fcn1)
        if self.element["module"] and "method" in self.element:
            if hasattr(self.element["module"], self.element["method"]):
                self.callback = getattr(self.element["module"], self.element["method"])
                fcn2 = lambda: self.second_callback()
                self.clicked.connect(fcn2)
            else:
               print("Error! Method " + self.element["method"] + " not found!")

    def set(self):
        group  = self.element["variable_group"]
        name   = self.element["variable"]
        val    = self.gui.getvar(group, name)
        # self.string = str(val)
        # self.setText(str(val))
        # self.setStyleSheet("")

    def first_callback(self):
        self.okay = True
        group = self.element["variable_group"]
        name  = self.element["variable"]
        val   = self.gui.getvar(group, name)
        if not val:
            val = os.getcwd()
        fname = QFileDialog.getOpenFileName(self, self.element["title"], val, self.element["filter"])
        if len(fname[0])>0:
            self.gui.setvar(group, name, fname[0])
        else:
            self.okay = False

    def second_callback(self):
        try:
            if self.okay:
                group = self.element["variable_group"]
                name  = self.element["variable"]
                val   = self.gui.getvar(group, name)
                self.callback(val, self)
                # Update GUI
                self.gui.update()
        except:
            traceback.print_exc()
