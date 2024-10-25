from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

class PopupMenu(QComboBox):
    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element

        if element.option_string.variable:
            group = element.option_string.variable_group
            name  = element.option_string.variable
            v     = element.getvar(group, name)
            for txt in v:
                self.addItem(txt)
        else:
            for txt in element.option_string.list:
                self.addItem(txt)

        # Adjust list value types
        if element.option_value:
            if not type(element.option_value.variable):
                for i, val in enumerate(element.option_value.list):
                    if element.type == float:
                        element.option_value[i] = float(val)
                    elif element.type == int:
                        element.option_value[i] = int(val)

        if element.text:
            if isinstance(element.text, str):
                txt = element.text
            else:
                txt = self.element.getvar(element.text.variable_group, element.text.variable)    
            label = QLabel(txt, element.parent.widget)
            label.setStyleSheet("background: transparent; border: none")
            self.text_widget = label

        if self.element.tooltip:
            if isinstance(self.element.tooltip, str):
                txt = self.element.tooltip
            else:
                txt = self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable)    
            self.setToolTip(txt)

        self.currentIndexChanged.connect(self.callback)

        self.set_geometry()

        self.execute_callback = True

    def showEvent(self, event):
        # Call when this widget becomes visible. This was commented out for the frame widget. Doing the same here. Not sure why this was needed.
        # self.set_geometry()
        pass

    def set(self):

        self.execute_callback = False

        if self.element.option_string.variable:
            self.add_items()

        if self.element.select == "item":
            if self.element.option_value:
                if self.element.option_value.variable:
                    name  = self.element.option_value.variable
                    group = self.element.option_value.variable_group
                    self.element.option_value.list = self.element.getvar(group, name)

            val = self.element.getvar(self.element.variable_group, self.element.variable)
            if val:
                if self.element.option_value:
                    index = self.element.option_value.list.index(val)
                    self.setCurrentIndex(index)
        else:
            name = self.element.variable
            group = self.element.variable_group
            index = self.element.getvar(group, name)
            self.setCurrentIndex(index)

        if not isinstance(self.element.text, str):
            txt = self.element.getvar(self.element.text.variable_group, self.element.text.variable)
            self.text_widget.setText(txt)

        if not isinstance(self.element.tooltip, str):
            txt = self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable)    
            self.setToolTip(txt)

        self.execute_callback = True

    def callback(self):

        if not self.execute_callback:
            return
        
        i = self.currentIndex()
        if self.element.select == "item":
            newval = self.element.option_value.list[i]
        else:
            newval = i

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
