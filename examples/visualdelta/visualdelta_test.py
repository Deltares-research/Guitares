"""
Example visualdelta
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

from visualdelta import visualdelta

if __name__ == '__main__':

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    # Show the splash screen
    visualdelta.gui.show_splash()

    # Initialize visualdelta, set gui variables
    visualdelta.initialize()

    # And build the GUI
    visualdelta.gui.build(app)

    # Close the splash screen
    visualdelta.gui.close_splash()

    app.exec_()
