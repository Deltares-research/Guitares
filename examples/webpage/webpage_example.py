"""
Example calculator
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

from webpage_comparison import wpc

if __name__ == '__main__':

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    # Initialize calculator, set gui variables
    wpc.initialize()

    # And build the GUI
    wpc.gui.build(app)

    app.exec_()
