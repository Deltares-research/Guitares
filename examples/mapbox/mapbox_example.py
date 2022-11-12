# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from mpbox import mpbox

if __name__ == '__main__':

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    # And build the GUI
    mpbox.gui.build(app)

    app.exec_()
