from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets

from guitares.gui import get_position

class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, view, print_messages):
        super().__init__(view)
        self.print_messages = print_messages
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if self.print_messages:
            print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)


class WebPage(QtWidgets.QWidget):
    def __init__(self, element, parent, gui):
        super().__init__(parent)

        self.gui = gui

        view = self.view = QtWebEngineWidgets.QWebEngineView(parent)

        x0, y0, wdt, hgt = get_position(element["position"], parent, self.gui.resize_factor)
        view.setGeometry(x0, y0, wdt, hgt)

        page = WebEnginePage(view, self.gui.js_messages)
        view.setPage(page)

        view.load(QtCore.QUrl(element["url"]))

    def set(self):
        pass
