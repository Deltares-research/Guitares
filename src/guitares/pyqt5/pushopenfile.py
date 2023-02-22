import os
from PyQt5.QtWidgets import QPushButton, QLabel, QFileDialog
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class PushOpenFile(QPushButton):

    def __init__(self, element):
        super().__init__(element.text, element.parent.widget)

        self.element = element

        self.setVisible(True)

        x0, y0, wdt, hgt = element.get_position()
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

        self.clicked.connect(self.callback)

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
        fname = QFileDialog.getOpenFileName(self, self.element.title, val, self.element.filter)
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
