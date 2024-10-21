import os
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QPushButton
from PyQt5 import QtCore, QtGui
import traceback

class Frame(QFrame):
    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element

        collapsable = False

        if element.collapse:
            # Parent
            collapsable = True
            # Add pushbutton to collapse
            self.pushbutton = QPushButton("", self)
            self.pushbutton.clicked.connect(self.collapse_callback)

        if hasattr(element.parent, "style"):
            if element.parent.style == "panel" and element.parent.collapse:
                collapsable = True

        if collapsable:
            self.setLineWidth(0)
        else:
            # Regular
            self.setFrameShape(QFrame.StyledPanel)
            self.setLineWidth(2)

        if element.text:
            self.text_widget = QLabel(element.text, element.parent.widget)

        self.set_geometry()

    def set(self):
        pass

    def showEvent(self, event):
        # What is this for? It was added by Daley at some point.
        # Setting the geometry at this point makes frames disappear because the size of the parent is 0,0,-1,-1 for some reason.
        # Comment out for now
        # self.set_geometry()
        pass

    def set_geometry(self):

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
            self.text_widget.setGeometry(int(x0 + 5*rf), int(y0 - 0.6*hlab), wlab, hlab)
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
        collapsable = False
        if hasattr(self.element.parent, "style"):
            if self.element.parent.style == "panel" and self.element.parent.collapse:
                pwdt = self.element.parent.widget.geometry().width() - button_size
                phgt = self.element.parent.widget.geometry().height()
                if self.element.parent.collapsed:
                    arrow_file = "icons8-triangle-arrow-16_white_left.png"
                else:
                    arrow_file = "icons8-triangle-arrow-16_white_right.png"                    
                self.element.parent.widget.pushbutton.setStyleSheet(
                    "background-image : url(:/img/" + arrow_file + "); border: none")

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

    def collapse_callback(self):
        try:
            if self.element.collapsed:
                self.element.collapsed = False
            else:
                self.element.collapsed = True
            self.element.gui.window.resize_elements(self.element.parent.elements)
            if self.element.callback:
                self.element.callback(self)
                # Update GUI
                self.element.window.update()
        except:
            traceback.print_exc()
