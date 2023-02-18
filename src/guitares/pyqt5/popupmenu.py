from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class PopupMenu(QComboBox):
    def __init__(self, element, parent, gui):
        super().__init__(parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        try:
            if "option_string" in element:
                if type(element["option_string"]) == dict:
                    group = element["option_string"]["variable_group"]
                    name  = element["option_string"]["variable"]
                    v     = gui.getvar(group, name)
                    for txt in v:
                        self.addItem(txt)
                else:
                    for txt in element["option_string"]:
                        self.addItem(txt)

            # Adjust list value types
            if element["option_value"]:
                if not type(element["option_value"]) == dict:
                    for i, val in enumerate(element["option_value"]):
                        if element["type"] == float:
                            element["option_value"][i] = float(val)
                        elif element["type"] == int:
                            element["option_value"][i] = int(val)
        except:
            print("Error setting popup menu for variable ..." )

        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)

        self.setGeometry(x0, y0, wdt, hgt)
        if element["text"]:
            label = QLabel(element["text"], parent)
            fm = label.fontMetrics()
            wlab = fm.size(0, element["text"]).width()
            if element["text_position"] == "above-center" or element["text_position"] == "above":
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setGeometry(x0, y0 - 20, wdt, 20)
            elif element["text_position"] == "above-left":
                label.setAlignment(QtCore.Qt.AlignLeft)
                label.setGeometry(x0, y0 - 20, wlab, 20)
            else:
                # Assuming left
                label.setAlignment(QtCore.Qt.AlignRight)
                label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, 20)
            label.setStyleSheet("background: transparent; border: none")
            self.text_widget = label

        fcn = lambda: self.first_callback()
        self.currentIndexChanged.connect(fcn)
        if element["module"] and "method" in element:
            if hasattr(element["module"], element["method"]):
                self.callback = getattr(element["module"], element["method"])
                fcn2 = lambda: self.second_callback()
                self.currentIndexChanged.connect(fcn2)
            else:
               print("Error! Method " + element["method"] + " not found!")

    def set(self):
        if self.element["option_value"]:
            if type(self.element["option_value"]) == dict:
                name  = self.element["option_value"]["variable"]
                group = self.element["option_value"]["variable_group"]
                self.element["option_value"] = self.gui.getvar(group, name)

        val = self.gui.getvar(self.element["variable_group"], self.element["variable"])
        if val:
            if self.element["option_value"]:
                index = self.element["option_value"].index(val)
                self.setCurrentIndex(index)

    def first_callback(self):
        i = self.currentIndex()
        newval = i
        if self.element["option_value"]:
            newval = self.element["option_value"][i]
        name  = self.element["variable"]
        group = self.element["variable_group"]
        self.gui.setvar(group, name, newval)

    def second_callback(self):
        try:
            if self.isEnabled():
                group = self.element["variable_group"]
                name  = self.element["variable"]
                val   = self.gui.getvar(group, name)
                self.callback(val, self)
                # Update GUI
                self.gui.update()
        except:
            traceback.print_exc()
