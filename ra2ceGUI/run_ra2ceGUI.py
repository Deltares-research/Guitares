"""
RA2CE GUI
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui

from ra2ceGUI import Ra2ceGUI


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    # Set the icon
    app.setWindowIcon(QtGui.QIcon('icons/deltares.ico'))

    # Show the splash screen
    Ra2ceGUI.gui.show_splash()

    # Initialize ra2ceGUI, set gui variables
    Ra2ceGUI.initialize()

    # And build the GUI
    Ra2ceGUI.gui.build(app)

    # Close the splash screen
    Ra2ceGUI.gui.close_splash()

    app.exec_()
