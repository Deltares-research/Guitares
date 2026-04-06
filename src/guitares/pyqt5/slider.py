"""PyQt5 horizontal slider widget with tick labels."""

import traceback
from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSlider


class Slider(QSlider):
    """Horizontal slider bound to a GUI variable.

    Parameters
    ----------
    element : Any
        The GUI element descriptor with min/max, text label, and callback.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(Qt.Horizontal, parent=element.parent.widget)

        self.element = element

        minimum = element.minimum
        maximum = element.maximum
        interval = 10
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setTickInterval(interval)
        self.setSingleStep(1)
        self.setTickPosition(QSlider.TicksBelow)

        if element.text:
            label = QLabel(element.text, self.element.parent.widget)
            label.setStyleSheet("background: transparent; border: none")
            self.text_widget = label

        # set tick labels
        self.tick_label = []
        for ii, ticklabel in enumerate([minimum, maximum]):
            label = QLabel(str(ticklabel), self.parent)
            label.setStyleSheet("background: transparent; border: none")
            self.tick_widget.append(label)

        self.valueChanged.connect(self.first_callback)
        self.sliderReleased.connect(self.second_callback)

        self.set_geometry()

    def set(self) -> None:
        """Update the slider position from the bound variable."""
        group = self.element.variable_group
        name = self.element.variable
        val = self.element.getvar(group, name)
        self.setValue(val)

    def first_callback(self) -> None:
        """Handle value-changed events by updating the bound variable."""
        self.okay = True
        val = self.value()
        group = self.element.variable_group
        name = self.element.variable
        self.element.setvar(group, name, val)
        self.setValue(val)
        if self.slide_callback:
            self.slide_callback(val, self)

    def second_callback(self) -> None:
        """Handle slider-released events by invoking the element callback."""
        try:
            if self.isEnabled() and self.element.callback:
                group = self.element.variable_group
                name = self.element.variable
                val = self.element.getvar(group, name)
                self.element.callback(val, self)
                # Update GUI
                self.element.window.update()
        except Exception:
            traceback.print_exc()

    def set_geometry(self) -> None:
        """Set widget position and size, including text and tick labels."""
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)

        if self.element.text:
            label = self.text_widget
            fm = label.fontMetrics()
            wlab = fm.size(0, element.text).width() + 15
            label.setAlignment(Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)

        # set tick labels
        ticks = [x0, x0 + wdt]
        for ii, label in enumerate(self.tick_widget):
            fm = label.fontMetrics()
            hlab = fm.height()
            wlab = fm.width(label.text, label.fontInfo().pointSize())
            label.setAlignment(Qt.AlignHCenter)
            label.setAlignment(Qt.AlignTop)
            label.setGeometry(ticks[ii], y0 + hgt, wlab, hlab)
