"""PySide6 frame (group box) widget wrapper with optional collapse support."""

import traceback
from typing import Any

from PySide6 import QtCore
from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton


class Frame(QGroupBox):
    """Group box frame that can optionally collapse/expand its content.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this frame.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)

        self.element = element

        collapsible = False

        if element.collapse:
            # Parent
            collapsible = True
            # Add pushbutton to collapse
            self.pushbutton = QPushButton("", self)
            self.pushbutton.clicked.connect(self.collapse_callback)
            if element.collapsed:
                self.pushbutton.setToolTip("Show information panel")
            else:
                self.pushbutton.setToolTip("Hide information panel")

        if hasattr(element.parent, "style"):
            if element.parent.style == "panel" and element.parent.collapse:
                collapsible = True

        if collapsible:
            pass
        else:
            pass

        if element.text:
            self.text_widget = QLabel(element.text, element.parent.widget)

        self.set_geometry()

    def set(self) -> None:
        """Update the frame (currently a no-op)."""
        pass

    def showEvent(self, event: Any) -> None:
        """Handle show event (currently a no-op).

        Parameters
        ----------
        event : Any
            The Qt show event.
        """
        pass

    def set_geometry(self) -> None:
        """Position and size the frame, its label, and collapse button."""
        rf = self.element.gui.resize_factor
        button_size = 12
        x0, y0, wdt, hgt = self.element.get_position()
        if self.element.collapse:
            wdt = wdt + button_size
        self.setGeometry(x0, y0, wdt, hgt)

        # Text widget
        if self.element.text:
            fm = self.text_widget.fontMetrics()
            hlab = fm.size(0, self.element.text).height()
            wlab = fm.size(0, self.element.text).width()
            self.text_widget.setGeometry(
                int(x0 + 5 * rf), int(y0 - 0.6 * hlab), wlab, hlab
            )
            self.text_widget.setAlignment(QtCore.Qt.AlignTop)

        # Push button
        button_size = 16
        if self.element.collapse:
            wdtp = button_size
            hgtp = button_size
            x0p = wdt - button_size
            y0p = int(0.5 * hgt - 0.5 * hgtp)
            self.pushbutton.setGeometry(x0p, y0p, wdtp, hgtp)

        # Check if these are collapable panels
        if hasattr(self.element.parent, "style"):
            if self.element.parent.style == "panel" and self.element.parent.collapse:
                pwdt = self.element.parent.widget.geometry().width() - button_size
                phgt = self.element.parent.widget.geometry().height()
                if self.element.parent.collapsed:
                    arrow_file = "icons8-triangle-arrow-16_white_left.png"
                else:
                    arrow_file = "icons8-triangle-arrow-16_white_right.png"
                self.element.parent.widget.pushbutton.setStyleSheet(
                    f"QPushButton {{ background-image: url(:/img/{arrow_file}); background-color: transparent; border: none; }}"
                    " QToolTip { color: #fff; background-color: #333; border: 1px solid #555; padding: 4px; }"
                )

                if self.element == self.element.parent.elements[0]:
                    # First panel
                    x0 = 0
                    y0 = 0
                    if self.element.parent.collapsed:
                        wdt = int(self.element.parent.fraction_collapsed * pwdt)
                    else:
                        wdt = int(self.element.parent.fraction_expanded * pwdt)
                    hgt = phgt
                else:
                    # Second panel
                    if self.element.parent.collapsed:
                        x0 = int(self.element.parent.fraction_collapsed * pwdt)
                    else:
                        x0 = int(self.element.parent.fraction_expanded * pwdt)
                    y0 = 0
                    wdt = pwdt - x0
                    hgt = phgt
                self.setGeometry(x0, y0, wdt, hgt)

    def collapse_callback(self) -> None:
        """Toggle the collapsed state and fire the element callback."""
        try:
            if self.element.collapsed:
                self.element.collapsed = False
                self.pushbutton.setToolTip("Hide information panel")
            else:
                self.element.collapsed = True
                self.pushbutton.setToolTip("Show information panel")
            self.element.gui.window.resize_elements(self.element.parent.elements)
            if self.element.callback:
                self.element.callback(self)
                # Update GUI
                self.element.window.update()
        except Exception:
            traceback.print_exc()
