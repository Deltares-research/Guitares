from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QLabel, QAbstractSpinBox
from PySide6 import QtCore
import traceback


class SpinBox(QAbstractSpinBox):
    """Spinbox widget supporting both int (QSpinBox) and float (QDoubleSpinBox).

    YAML config keys:
        minimum       : lower bound (default 0)
        maximum       : upper bound (default 100)
        step          : step size per click (default 1 for int, 0.1 for float)
        decimals      : decimal places shown, float only (default 2)
        suffix        : unit string appended to value, e.g. " m" (default "")
        text          : label string or {variable, variable_group}
        text_position : "left" (default) | "above" | "above-center" | "above-left" | "right"
        tooltip       : tooltip string or {variable, variable_group}
    """

    def __init__(self, element):
        # Instantiate the correct Qt spinbox based on variable type
        if element.type == float:
            self._spinbox = QDoubleSpinBox(element.parent.widget)
            self._spinbox.setDecimals(element.decimals)
            self._spinbox.setSingleStep(element.step if element.step is not None else 0.1)
        else:
            self._spinbox = QSpinBox(element.parent.widget)
            self._spinbox.setSingleStep(int(element.step) if element.step is not None else 1)

        self._spinbox.setMinimum(element.minimum)
        self._spinbox.setMaximum(element.maximum)

        if element.suffix:
            self._spinbox.setSuffix(element.suffix)

        if not element.enable:
            self._spinbox.setEnabled(False)

        self.element = element

        # Label
        self.text_widget = None
        if element.text:
            if isinstance(element.text, str):
                txt = element.text
            else:
                txt = element.getvar(element.text.variable_group, element.text.variable)
            label = QLabel(txt, element.parent.widget)
            label.setStyleSheet("background: transparent; border: none")
            if not element.enable:
                label.setEnabled(False)
            self.text_widget = label
            label.setVisible(True)

        # Tooltip
        if element.tooltip:
            if isinstance(element.tooltip, str):
                txt = element.tooltip
            else:
                txt = element.getvar(element.tooltip.variable_group, element.tooltip.variable)
            self._spinbox.setToolTip(txt)

        self._spinbox.valueChanged.connect(self._on_value_changed)
        self._spinbox.editingFinished.connect(self._on_editing_finished)

        self._suppress_callback = False

        self.set_geometry()
        self._spinbox.setVisible(True)

    # ------------------------------------------------------------------
    # Public interface expected by Guitares (set, set_geometry, setVisible,
    # setEnabled, isEnabled, geometry)
    # ------------------------------------------------------------------

    def set(self):
        self._suppress_callback = True
        group = self.element.variable_group
        name = self.element.variable
        val = self.element.getvar(group, name)
        if val is not None:
            self._spinbox.setValue(val)

        if self.text_widget and not isinstance(self.element.text, str):
            txt = self.element.getvar(self.element.text.variable_group, self.element.text.variable)
            self.text_widget.setText(txt)

        if self.element.tooltip and not isinstance(self.element.tooltip, str):
            txt = self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable)
            self._spinbox.setToolTip(txt)

        self._suppress_callback = False

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self._spinbox.setGeometry(x0, y0, wdt, hgt)

        if self.text_widget:
            label = self.text_widget
            fm = label.fontMetrics()
            if isinstance(self.element.text, str):
                txt = self.element.text
            else:
                txt = self.element.getvar(self.element.text.variable_group, self.element.text.variable)
            wlab = int(fm.size(0, txt).width())

            pos = self.element.text_position
            if pos in ("above-center", "above"):
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setGeometry(x0, int(y0 - 20 * resize_factor), wdt, int(20 * resize_factor))
            elif pos == "above-left":
                label.setAlignment(QtCore.Qt.AlignLeft)
                label.setGeometry(x0, int(y0 - 20 * resize_factor), wlab, int(20 * resize_factor))
            elif pos == "right":
                label.setAlignment(QtCore.Qt.AlignLeft)
                label.setGeometry(
                    int(x0 + wdt + 3 * resize_factor),
                    int(y0 + 5 * resize_factor),
                    wlab,
                    int(20 * resize_factor),
                )
            else:
                # default: left
                label.setAlignment(QtCore.Qt.AlignRight)
                label.setGeometry(
                    int(x0 - wlab - 3 * resize_factor),
                    int(y0 + 5 * resize_factor),
                    wlab,
                    int(20 * resize_factor),
                )

    # Proxy visibility / enable so Guitares can call these on self.widget
    def setVisible(self, visible):
        self._spinbox.setVisible(visible)
        if self.text_widget:
            self.text_widget.setVisible(visible)

    def setEnabled(self, enabled):
        self._spinbox.setEnabled(enabled)
        if self.text_widget:
            self.text_widget.setEnabled(enabled)

    def isEnabled(self):
        return self._spinbox.isEnabled()

    def geometry(self):
        return self._spinbox.geometry()

    # ------------------------------------------------------------------
    # Internal callbacks
    # ------------------------------------------------------------------

    def _on_value_changed(self, val):
        # Keep the variable store in sync while the user is spinning, but
        # do not fire the user callback until editing is finished.
        if self._suppress_callback:
            return
        group = self.element.variable_group
        name = self.element.variable
        self.element.setvar(group, name, val)

    def _on_editing_finished(self):
        if self._suppress_callback:
            return
        try:
            if self._spinbox.isEnabled() and self.element.callback:
                group = self.element.variable_group
                name = self.element.variable
                val = self.element.getvar(group, name)
                self.element.callback(val, self)
            self.element.window.update()
        except Exception:
            traceback.print_exc()
