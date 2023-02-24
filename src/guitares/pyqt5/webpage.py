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

        view = self.view = QtWebEngineWidgets.QWebEngineView(element.parent.widget)

        x0, y0, wdt, hgt = element.get_position()
        view.setGeometry(x0, y0, wdt, hgt)

        page = WebEnginePage(view, element.gui.js_messages)
        view.setPage(page)

        view.load(QtCore.QUrl(element.url))

    def set(self):
        pass
