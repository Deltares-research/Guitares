"""PySide6 radio button group widget wrapper for Guitares GUI elements."""

import traceback
from typing import Any

from PySide6.QtWidgets import QButtonGroup, QRadioButton


class RadioButtonGroup(QButtonGroup):
    """Group of mutually exclusive radio buttons linked to a Guitares variable.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this radio button group.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)

        self.element = element

        if element.option_value.variable:
            group = element.option_value.variable_group
            name = element.option_value.variable
            self.element.option_value.list = element.getvar(group, name)
        if element.option_string.variable:
            group = element.option_string.variable_group
            name = element.option_string.variable
            self.element.option_string.list = element.getvar(group, name)
        for i in range(len(self.element.option_value.list)):
            d = QRadioButton(
                self.element.option_string.list[i], self.element.parent.widget
            )
            d.setVisible(True)
            d.id = i
            self.addButton(d)
            self.buttonClicked.connect(self.callback)

        self.set_geometry()

    def set(self) -> None:
        """Select the radio button matching the current variable value."""
        group = self.element.variable_group
        name = self.element.variable
        val = self.element.getvar(group, name)
        values = self.element.option_value.list
        indx = values.index(val)
        self.buttons()[indx].setChecked(True)

    def callback(self, button: QRadioButton) -> None:
        """Handle radio button selection and fire the element callback.

        Parameters
        ----------
        button : QRadioButton
            The radio button that was clicked.
        """
        group = self.element.variable_group
        name = self.element.variable
        values = self.element.option_value.list

        if self.element.getvar(group, name) == values[button.id]:
            # Value has not changed
            return

        self.element.setvar(group, name, values[button.id])

        try:
            if self.element.callback:
                self.element.callback(values[button.id], self)
                # Update GUI
                self.element.window.update()
        except Exception:
            traceback.print_exc()

    def set_geometry(self) -> None:
        """Position and size the radio buttons vertically."""
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        nbuttons = len(self.element.option_value.list)
        # Lower y of top button
        yll = y0 + hgt - int(nbuttons * 20 * resize_factor)
        for i in range(nbuttons):
            self.buttons()[i].setGeometry(
                x0, int(yll + i * 20 * resize_factor), wdt, int(20 * resize_factor)
            )

    def set_enabled(self, true_or_false: bool) -> None:
        """Enable or disable all radio buttons.

        Parameters
        ----------
        true_or_false : bool
            Whether to enable the buttons.
        """
        nbuttons = len(self.element.option_value.list)
        for i in range(nbuttons):
            self.buttons()[i].setEnabled(true_or_false)

    def set_visible(self, true_or_false: bool) -> None:
        """Show or hide all radio buttons.

        Parameters
        ----------
        true_or_false : bool
            Whether to show the buttons.
        """
        nbuttons = len(self.element.option_value.list)
        for i in range(nbuttons):
            self.buttons()[i].setVisible(true_or_false)
