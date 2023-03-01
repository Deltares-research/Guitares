# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.

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

        self.callback_module = element["module"]
