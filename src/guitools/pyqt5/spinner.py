from pyqtspinner import WaitingSpinner
from PyQt5.QtWidgets import QWidget

from .widget_group import WidgetGroup


class Spinner(WidgetGroup):
    def __init__(self, element, parent):
        super().__init__(element, parent)

        b = QWidget()
        self.widgets.append(b)

        self.spinner = WaitingSpinner(parent)

    def start(self):
        self.spinner.start()

    def stop(self):
        self.spinner.stop()
