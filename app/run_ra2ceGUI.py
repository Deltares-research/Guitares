"""
RA2CE GUI
"""

import logging
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui

from app.logger import Ra2ceGUILogger
from app.ra2ceGUI_base import Ra2ceGUI


if __name__ == "__main__":
    try:
        Ra2ceGUILogger(logging_dir='.', logger_name="RA2CE_GUI")

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
    except BaseException as e:
        logging.exception(
            f"The RA2CE GUI crashed. Check the logfile for the Traceback message: {e}"
        )
