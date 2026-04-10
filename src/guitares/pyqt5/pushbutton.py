"""PyQt5 push button widget with optional icon and colormap support."""

import traceback
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QPushButton


class PushButton(QPushButton):
    """Push button with optional icon, colormap visualization, and callback.

    Parameters
    ----------
    element : Any
        The GUI element descriptor with text, icon, colormap, and callback info.
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
        """Update button text, tooltip, and colormap icon from bound variables."""
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
        """Handle button click events."""
        try:
            if self.element.callback and self.underMouse():
                self.element.callback(self)
                # Update GUI
                self.element.window.update()
        except Exception:
            traceback.print_exc()

    def set_geometry(self) -> None:
        """Set widget position and size from the element descriptor."""
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)

    def update_colormap_icon(self) -> None:
        """Update the button icon to show the current matplotlib colormap."""
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
        self.setIcon(icon)
        icon_size = QSize(wdt, hgt)
        self.setGeometry(x0, y0, wdt, hgt)
        self.setIconSize(icon_size)

    def create_icon_from_colormap(self, cmap: Any, wdt: int, hgt: int) -> QIcon:
        """Create a QIcon showing a horizontal gradient of a matplotlib colormap.

        Parameters
        ----------
        cmap : Any
            A matplotlib colormap object.
        wdt : int
            The icon width in pixels.
        hgt : int
            The icon height in pixels.

        Returns
        -------
        QIcon
            The generated colormap icon.
        """
        gradient = np.linspace(0, 1.0, wdt)
        gradient = np.tile(gradient, (hgt, 1))
        img = cmap(gradient)

        # Convert the image to a QPixmap
        img = np.uint8(img * 255)
        qimage = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)

        return QIcon(pixmap)
