from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore

from .widget_group import WidgetGroup

#from gui import getvar, setvar

class ListBox(WidgetGroup):

    def __init__(self, element, parent):
        super().__init__(element, parent)

        b = QListWidget(parent)
        self.widgets.append(b)

        self.add_items()

        # Adjust list value types
#        if self.element["option_value"]:
        if self.element["select"] == "item":
            if not type(self.element["option_value"]) == dict:
                for i, val in enumerate(self.element["option_value"]):
                    if self.element["type"] == float:
                        self.element["option_value"][i] = float(val)
                    elif self.element["type"] == int:
                        self.element["option_value"][i] = int(val)
            # else:
            #     group = self.element["option_value"]["variable_group"]
            #     name  = self.element["option_value"]["variable"]
            #     v = variables[self.element["option_value"]]

        x0, y0, wdt, hgt = element["window"].get_position_from_string(self.element["position"], self.parent)
        b.setGeometry(x0, y0, wdt, hgt)
        if element["text"]:
            label = QLabel(self.element["text"], self.parent)
            self.widgets.append(label)
            fm = label.fontMetrics()
            wlab = fm.size(0, self.element["text"]).width() + 15
            label.setAlignment(QtCore.Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")

        fcn = lambda: self.callback()
#        b.currentItemChanged.connect(fcn)
        b.clicked.connect(fcn)
        if self.element["module"] and "method" in self.element:
            fcn = getattr(self.element["module"], self.element["method"])
            b.clicked.connect(fcn)

    def set(self):

        if self.check_variables():

            # First check if items need to be updated. This is only necessary when "option_string" is a dict
            if type(self.element["option_string"]) == dict:
                self.add_items()

            # Get the items
            items = []
            for x in range(self.widgets[0].count()):
                items.append(self.widgets[0].item(x))

            # Get value
            getvar = self.element["getvar"]
            val = getvar(self.element["variable_group"], self.element["variable"])

            # Now get the values
            if self.element["select"] == "item":
                if type(self.element["option_value"]) == dict:
                    getvar = self.element["getvar"]
                    name  = self.element["option_value"]["variable"]
                    group = self.element["option_value"]["variable_group"]
                    vals = getvar(group, name)
                    if not vals:
                        vals = [""]
                else:
                    vals = self.element["option_value"]

                if val in vals:
                    index = vals.index(val)
                else:
                    index = 0
                    print(self.element["variable"] + ' not found !')

            else:
                index = val

            self.widgets[0].setCurrentItem(items[index])

            self.set_dependencies()

    def callback(self):

        if self.check_variables():

            index = self.widgets[0].currentRow()

            if type(self.element["option_value"]) == dict:
                getvar = self.element["getvar"]
                name = self.element["option_value"]["variable"]
                group = self.element["option_value"]["variable_group"]
                vals = getvar(group, name)
                if not vals:
                    vals = [""]
            else:
                vals = self.element["option_value"]

            if self.element["select"] == "item":
                newval = vals[index]
            else:
                newval = index

            setvar = self.element["setvar"]
            name  = self.element["variable"]
            group = self.element["variable_group"]
            setvar(group, name, newval)

    def add_items(self):

        # Delete existing items
        self.widgets[0].clear()

        if type(self.element["option_string"]) == dict:
            getvar = self.element["getvar"]
            group = self.element["option_string"]["variable_group"]
            name = self.element["option_string"]["variable"]
            v = getvar(group, name)
            if not v:
                v = [""]
            for itxt, txt in enumerate(v):
                self.widgets[0].insertItem(itxt, txt)
        else:
            for itxt, txt in enumerate(self.element["option_string"]):
                self.widgets[0].insertItem(itxt, txt)
