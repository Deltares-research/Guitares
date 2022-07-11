"""
Example calculator
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

from calculator import calculator

if __name__ == '__main__':

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    # Show the splash screen
    calculator.gui.show_splash()

    # Initialize calculator, set gui variables
    calculator.initialize()

    # And build the GUI
    calculator.gui.build(app)

    # Close the splash screen
    calculator.gui.close_splash()

    app.exec_()
