from PyQt5.QtWidgets import QSlider, QLabel
from PyQt5.QtCore import Qt

from .widget_group import WidgetGroup

#from gui import getvar, setvar

class Slider(WidgetGroup):

    def __init__(self, element, parent):
        super().__init__(element, parent)

        # s = QSlider(parent)
        s = QSlider(Qt.Horizontal, parent=parent)
        #ToDO: Make minimum and maximum flexible
        s.setMinimum(2000)
        s.setMaximum(2300)
        s.setTickInterval(1)
        s.setSingleStep(1)
        s.setTickPosition(QSlider.TicksBothSides)
        self.widgets.append(s)

        x0, y0, wdt, hgt = element["window"].get_position_from_string(self.element["position"], self.parent)
        s.setGeometry(x0, y0, wdt, hgt)
        if element["text"]:
            label = QLabel(self.element["text"], self.parent)
            self.widgets.append(label)
            fm = label.fontMetrics()
            wlab = fm.size(0, self.element["text"]).width() + 15
            label.setAlignment(Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")

        fcn = lambda: self.callback()
        s.valueChanged.connect(fcn)
        if self.element["module"] and "method" in self.element:
            fcn = getattr(self.element["module"], self.element["method"])
            s.valueChanged.connect(fcn)

    def set(self):
        if self.check_variables():
            getvar = self.element["getvar"]
            group  = self.element["variable_group"]
            name   = self.element["variable"]
            val    = getvar(group, name)
            self.widgets[0].setValue(val)
            self.set_dependencies()

    def callback(self):
        self.okay = True
        if self.check_variables():
            newval = self.widgets[0].value()

            # Update value in variable dict
            if self.okay:
                setvar = self.element["setvar"]
                group  = self.element["variable_group"]
                name   = self.element["variable"]
                setvar(group, name, newval)
                self.widgets[0].setValue(newval)