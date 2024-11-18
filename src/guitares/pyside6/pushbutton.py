from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon, QPixmap, QColor, QImage
from PySide6.QtCore import QSize
import traceback
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt

class PushButton(QPushButton):

    def __init__(self, element):
        super().__init__("", element.parent.widget)

        self.element = element

        self.clicked.connect(self.callback)

        if element.icon:
            self.setIcon(QIcon(element.icon))

        if element.colormap:
            self.update_colormap_icon()

        if element.text:
            if type(element.text) is str:
                txt = element.text
            else:
                txt = self.element.getvar(element.text.variable_group, element.text.variable)    
            self.setText(txt)    

        if self.element.tooltip:
            if type(self.element.tooltip) is str:
                txt = self.element.tooltip
            else:
                txt = self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable)    
            self.setToolTip(txt)

        self.set_geometry()

    def set(self):
        if type(self.element.text) is not str:
            self.setText(self.element.getvar(self.element.text.variable_group, self.element.text.variable))   
        if type(self.element.tooltip) is not str:
            self.setToolTip(self.element.getvar(self.element.tooltip.variable_group, self.element.tooltip.variable))
        if hasattr(self, "colormap"):
            self.update_colormap_icon()


    def callback(self):
        try:
            if self.element.callback and self.underMouse():
                self.element.callback(self)
                # Update GUI
                self.element.window.update()
        except:
            traceback.print_exc()

    def set_geometry(self):
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)

    def update_colormap_icon(self):
        if type(self.element.colormap) is str:
            self.colormap = self.element.colormap
        else:
            self.colormap = self.element.getvar(self.element.colormap.variable_group, self.element.colormap.variable)
        cmap = plt.get_cmap(self.colormap) 
        x0, y0, wdt, hgt = self.element.get_position()
        # Create a QIcon from the colormap
        icon = self.create_icon_from_colormap(cmap, wdt, hgt)            
        # Set the icon on the button
        self.setIcon(icon)            
        # Set the icon size
        icon_size = QSize(wdt, hgt)  # Adjust the size as needed
        self.setGeometry(x0, y0, wdt, hgt)
        self.setIconSize(icon_size)

    def create_icon_from_colormap(self, cmap, wdt, hgt):
        # Create a gradient image
        gradient = np.linspace(0, 1.0, wdt)
        gradient = np.tile(gradient, (hgt, 1))
        # gradient = np.vstack((gradient, gradient))
        img = cmap(gradient)

        # Convert the image to a QPixmap
        img = np.uint8(img * 255)
        qimage = QImage(img.data, img.shape[1], img.shape[0], 
                        QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)

        # Create a QIcon from the QPixmap
        return QIcon(pixmap)