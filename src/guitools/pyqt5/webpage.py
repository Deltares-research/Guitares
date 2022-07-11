import os
import functools
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)


class WebPage(QtWidgets.QWidget):

    def __init__(self, element, parent):
        super().__init__(parent)

        view = self.view = QtWebEngineWidgets.QWebEngineView(parent)
        view.setGeometry(10, 10, 100, 100)

        page = WebEnginePage(view)
        view.setPage(page)

        view.load(QtCore.QUrl(element["url"]))

        element["widget"] = view

#        self.callback_module = element["module"]
