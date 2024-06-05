import os
from PyQt5.QtWidgets import QPushButton, QFileDialog
import traceback


class PushOpenDir(QPushButton):

    def __init__(self, element):
        super().__init__("", element.parent.widget)

        self.element = element

        if element.text:
            if isinstance(element.text, str):
                txt = element.text
            else:
                txt = self.element.getvar(
                    element.text.variable_group, element.text.variable
                )
            self.setText(txt)

        if self.element.tooltip:
            if isinstance(element.tooltip, str):
                txt = self.element.tooltip
            else:
                txt = self.element.getvar(
                    self.element.tooltip.variable_group, self.element.tooltip.variable
                )
            self.setToolTip(txt)

        self.setVisible(True)

        self.clicked.connect(self.callback)

        self.set_geometry()

    def set(self):
        if not isinstance(self.element.text, str):
            self.setText(
                self.element.getvar(
                    self.element.text.variable_group, self.element.text.variable
                )
            )
        if not isinstance(self.element.tooltip, str):
            self.setToolTip(
                self.element.getvar(
                    self.element.tooltip.variable_group, self.element.tooltip.variable
                )
            )

    def callback(self):
        self.okay = True
        group = self.element.variable_group
        name = self.element.variable
        val = self.element.getvar(group, name)
        if not val:
            val = os.getcwd()
        val = str(val).replace("\\", "/")
        dir_name = QFileDialog.getExistingDirectory(
            parent=self,
            caption=self.element.title,
            directory=val,
            options=QFileDialog.ShowDirsOnly,
        )
        if dir_name:
            self.element.setvar(group, name, dir_name)
        else:
            self.okay = False

        try:
            if self.okay and self.element.callback:
                self.element.callback(dir_name, self)
                self.element.window.update()
        except:
            traceback.print_exc()

    def set_geometry(self):
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
