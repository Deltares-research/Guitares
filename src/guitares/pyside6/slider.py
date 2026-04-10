"""PySide6 slider widget wrapper for Guitares GUI elements."""

import traceback
from typing import Any, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSlider


class Slider(QSlider):
    """Horizontal slider that syncs its value with a Guitares variable.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this slider.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(Qt.Horizontal, parent=element.parent.widget)

        self.element = element

        # ToDO: Make minimum and maximum flexible
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
        self.tick_label: List[QLabel] = []
        self.tick_widget: List[QLabel] = []
        for ii, ticklabel in enumerate([minimum, maximum]):
            label = QLabel(str(ticklabel), self.parent())
            label.setStyleSheet("background: transparent; border: none")
            self.tick_widget.append(label)

        self.valueChanged.connect(self.first_callback)
        self.sliderReleased.connect(self.second_callback)

        self.set_geometry()

    def set(self) -> None:
        """Update the slider position from the linked variable."""
        group = self.element.variable_group
        name = self.element.variable
        val = self.element.getvar(group, name)
        self.setValue(val)

    def first_callback(self) -> None:
        """Handle value change during sliding (updates variable continuously)."""
        self.okay = True
        val = self.value()
        # Update value in variable dict
        group = self.element.variable_group
        name = self.element.variable
        self.element.setvar(group, name, val)
        self.setValue(val)
        if self.slide_callback:
            self.slide_callback(val, self)

    def second_callback(self) -> None:
        """Handle slider release and fire the element callback."""
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
        """Position and size the slider, its label, and tick labels."""
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)

        if self.element.text:
            label = self.text_widget
            fm = label.fontMetrics()
            wlab = fm.size(0, self.element.text).width() + 15
            label.setAlignment(Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)

        # set tick labels
        ticks = [x0, x0 + wdt]
        for ii, label in enumerate(self.tick_widget):
            fm = label.fontMetrics()
            hlab = fm.height()
            wlab = fm.horizontalAdvance(label.text())
            label.setAlignment(Qt.AlignHCenter)
            label.setAlignment(Qt.AlignTop)
            label.setGeometry(ticks[ii], y0 + hgt, wlab, hlab)
