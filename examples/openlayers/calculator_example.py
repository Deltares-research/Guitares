"""
Example calculator
"""

import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

from calculator_gui import setvar, gui


class Calculator:

    def __init__(self):

        # Splash screen
        gui.show_splash()

        self.version = "1.0"
        self.source_path = os.path.dirname(__file__)

        # Define GUI variables
        setvar("calculator", "a", 1.0)
        setvar("calculator", "b", 2.0)
        setvar("calculator", "answer", 3.0)
        setvar("calculator", "operator", "plus")
        setvar("calculator", "operator_values", ["plus", "minus", "times", "divided_by"])
        setvar("calculator", "operator_strings", ["+", "-", "*", "/"])

        gui.initialize(config_file="calculator.yml")


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    calculator = Calculator()
    gui.close_splash()
    app.exec_()
