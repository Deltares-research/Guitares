"""PySide6 push button widget wrapper with optional colormap icon support."""

import traceback
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import QPushButton


class PushButton(QPushButton):
    """Push button that can display text, an icon, or a colormap preview.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this button.
    """

    def __init__(self, element: Any) -> None:
        super().__init__("", element.parent.widget)

        self.element = element

        self.clicked.connect(self.callback)

        if element.icon:
            self.setIcon(QIcon(element.icon))

        if element.colormap:
            self.update_colormap_icon()

        if element.text:
            if isinstance(element.text, str):
                txt = element.text
            else:
                txt = self.element.getvar(
                    element.text.variable_group, element.text.variable
                )
            self.setText(txt)

        if self.element.tooltip:
            if isinstance(self.element.tooltip, str):
                txt = self.element.tooltip
            else:
                txt = self.element.getvar(
                    self.element.tooltip.variable_group, self.element.tooltip.variable
                )
            self.setToolTip(txt)

        self.set_geometry()

    def set(self) -> None:
        """Update button text, tooltip, and colormap icon from the linked variables."""
        if not isinstance(self.element.text, str):
            self.setText(
                self.element.getvar(
                    self.element.text.variable_group, self.element.text.variable
                )
            )
        if not isinstance(self.element.tooltip, str):
            self.setToolTip(
                self.element.getvar(
                    self.element.tooltip.variable_group, self.element.tooltip.variable
                )
            )
        if hasattr(self, "colormap"):
            self.update_colormap_icon()

    def callback(self) -> None:
        """Handle button click and fire the element callback."""
        try:
            if self.element.callback and self.underMouse():
                self.element.callback(self)
                # Update GUI
                self.element.window.update()
        except Exception:
            traceback.print_exc()

    def set_geometry(self) -> None:
        """Position and size the button."""
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        self.setFixedSize(wdt, hgt)  # Set fixed size to prevent resizing

    def update_colormap_icon(self) -> None:
        """Regenerate the button icon from the current colormap name."""
        if isinstance(self.element.colormap, str):
            self.colormap = self.element.colormap
        else:
            self.colormap = self.element.getvar(
                self.element.colormap.variable_group, self.element.colormap.variable
            )
        cmap = plt.get_cmap(self.colormap)
        x0, y0, wdt, hgt = self.element.get_position()
        # Create a QIcon from the colormap
        icon = self.create_icon_from_colormap(cmap, wdt, hgt)
        # Set the icon on the button
        self.setIcon(icon)
        # Set the icon size
        icon_size = QSize(wdt, hgt)
        self.setGeometry(x0, y0, wdt, hgt)
        self.setIconSize(icon_size)

    def create_icon_from_colormap(self, cmap: Any, wdt: int, hgt: int) -> QIcon:
        """Create a QIcon showing a horizontal colormap gradient.

        Parameters
        ----------
        cmap : Any
            A matplotlib colormap object.
        wdt : int
            Width of the icon in pixels.
        hgt : int
            Height of the icon in pixels.

        Returns
        -------
        QIcon
            The generated colormap icon.
        """
        # Create a gradient image
        gradient = np.linspace(0, 1.0, wdt)
        gradient = np.tile(gradient, (hgt, 1))
        img = cmap(gradient)

        # Convert the image to a QPixmap
        img = np.uint8(img * 255)
        qimage = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)

        # Create a QIcon from the QPixmap
        return QIcon(pixmap)
