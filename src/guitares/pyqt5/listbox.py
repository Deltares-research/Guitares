from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class ListBox(QListWidget):

    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element
        resize_factor = element.gui.resize_factor

        self.add_items()

        # Adjust list value types
        if element.select == "item":
            if not self.element.option_value.variable:
                # List
                for i, val in enumerate(element.option_value):
                    if element.type == float:
                        element.option_value[i] = float(val)
                    elif element.type == int:
                        element.option_value[i] = int(val)

        if element.text:
            label = QLabel(element.text, element.parent.widget)

            label.setStyleSheet("background: transparent; border: none")

            self.text_widget = label

        # First call back to change the variable
        self.clicked.connect(self.callback)
#        self.itemSelectionChanged.connect(self.callback)
#        self.currentRowChanged.connect(self.callback)

        self.set_geometry()

    def set(self):

        current_index = self.currentRow() 

        # First check if items need to be updated. This is only necessary when "option_string" is a dict
        if self.element.option_string.variable:
            self.add_items()

        # Get the items
        items = []
        for x in range(self.count()):
            items.append(self.item(x))

        # Get value
        val = self.element.getvar(self.element.variable_group, self.element.variable)

        # Now get the values
        if self.element.select == "item":
            if self.element.option_value.variable:
                name  = self.element.option_value.variable
                group = self.element.option_value.variable_group
                vals = self.element.getvar(group, name)
                if not vals:
                    vals = [""]
            else:
                vals = self.element.option_value.list

            if val in vals:
                index = vals.index(val)
            else:
                index = 0
                print(self.element.variable + ' not found !')

        else:
            index = val

        # print("current_index=" + str(current_index))
        # print("index=" + str(index))
        # if index != current_index:
        self.setCurrentItem(items[index])

    def callback(self):
        index = self.currentRow()
        if self.element.select == "item":
            if self.element.option_value.variable:
                name = self.element.option_value.variable
                group = self.element.option_value.variable_group
                vals = self.element.getvar(group, name)
                if not vals:
                    vals = [""]
            else:
                vals = self.element.option_value.list
            newval = vals[index]
        else:
            newval = index

        name  = self.element.variable
        group = self.element.variable_group
        self.element.setvar(group, name, newval)

        try:
            if self.isEnabled() and self.element.callback:
                self.element.callback(newval, self)
            # Update GUI
            self.element.window.update()
        except:
            traceback.print_exc()

    def add_items(self):
        # Delete existing items
        self.clear()
        if self.element.option_string.variable:
            group = self.element.option_string.variable_group
            name  = self.element.option_string.variable
            v     = self.element.getvar(group, name)
            if not v:
                v = [""]
            for itxt, txt in enumerate(v):
                self.insertItem(itxt, txt)
        else:
            for itxt, txt in enumerate(self.element.option_string.list):
                self.insertItem(itxt, txt)

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
