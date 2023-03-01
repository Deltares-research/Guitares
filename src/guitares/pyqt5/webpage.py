from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets

#from guitares.gui import get_position

class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, view, print_messages):
        super().__init__(view)
        self.print_messages = print_messages
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if self.print_messages:
            print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)


class WebPage(QtWidgets.QWidget):
    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element

        view = self.view = QtWebEngineWidgets.QWebEngineView(element.parent.widget)

        self.set_geometry()

        page = WebEnginePage(view, element.gui.js_messages)
        view.setPage(page)

        view.load(QtCore.QUrl(element.url))

    def set(self):
        pass

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.view.setGeometry(x0, y0, wdt, hgt)
