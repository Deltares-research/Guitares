"""
Example calculator
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from PyQt5 import QtWebEngineWidgets

from mapbox_example import mpbox

if __name__ == '__main__':

    mpbox.initialize()

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    # Initialize openlayers, set gui variables

    # And build the GUI
    mpbox.gui.build(app)

    app.exec_()
