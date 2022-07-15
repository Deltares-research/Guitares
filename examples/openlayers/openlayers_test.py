"""
Example calculator
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

from openlayers import olt

if __name__ == '__main__':

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    # Initialize openlayers, set gui variables
    olt.initialize()

    # And build the GUI
    olt.gui.build(app)

    app.exec_()
