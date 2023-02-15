import os
import copy

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtWidgets import QApplication

from guitools.gui import read_gui_config, set_missing_config_values, add_elements, resize_elements

class PopupWindow(QDialog):
    def __init__(self, config, gui, modal=True):
        super().__init__()

        self.resize_factor = 1.0

        if isinstance(config, str):
            # Config is a yml config file. Read it.
            # Read config yml file
            dir_name = os.path.dirname(config)
            file_name = os.path.basename(config)
            # Read element file
            config = read_gui_config(dir_name, file_name)

        # Set missing values
#        set_missing_config_values(config, gui.variables, gui.getvar, gui.setvar)
        self.config = config

        set_missing_config_values(self.config, gui)

        screen = QApplication.primaryScreen()
        if screen.size().width() > 2500:
            self.resize_factor = 1.4
        elif screen.size().width() > 1200:
            self.resize_factor = 1.4
        else:
            self.resize_factor = 1.0

        # Set position
        self.setWindowTitle(self.config["window"]["title"])
        self.window_width = int(self.config["window"]["width"]*self.resize_factor)
        self.window_height = int(self.config["window"]["height"]*self.resize_factor)
        self.setMinimumSize(self.window_width, self.window_height)
        self.setMaximumSize(self.window_width, self.window_height)
        screen = QApplication.primaryScreen()
        self.setGeometry(int(0.5*(screen.size().width() - self.window_width)),
                         int(0.5*(screen.size().height() - self.window_height)),
                         self.window_width,
                         self.window_height)
        self.setModal(modal)

        # Add elements
        cancel = {'style': 'pushbutton', 'text': 'Cancel', 'position': {'x': -80, 'y': 10, 'width': 50, 'height': 20}, 'method': self.cancel, 'dependency': [], 'enable': True}
        ok     = {'style': 'pushbutton', 'text': 'OK', 'position': {'x':  -20, 'y': 10, 'width': 50, 'height': 20}, 'method': self.ok, 'dependency': [], 'enable': True}

        self.config["element"].append(cancel)
        self.config["element"].append(ok)

        add_elements(self.config["element"], self, gui)

        gui.popup_config = self.config

        self.show()
        self.exec_()

    def ok(self):
        self.done(1)

    def cancel(self):
        self.done(0)

    def update(self):
        # Update all elements
        set_elements(self.config["element"])

    def resizeEvent(self, event):
        # There shouldn't be any resizing of pop-up windows ...
        resize_elements(self.config["element"], self, self.resize_factor)

    def closeEvent(self,event):
        pass
