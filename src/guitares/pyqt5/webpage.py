"""PyQt5 embedded web page widget using QWebEngineView."""

import logging
from typing import Any

from PyQt5 import QtCore, QtWebEngineWidgets, QtWidgets

logger = logging.getLogger(__name__)


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    """Custom web engine page that optionally prints JS console messages.

    Parameters
    ----------
    view : QtWebEngineWidgets.QWebEngineView
        The parent web engine view.
    """

    def __init__(self, view: QtWebEngineWidgets.QWebEngineView) -> None:
        super().__init__(view)

    def javaScriptConsoleMessage(
        self, level: int, message: str, lineNumber: int, sourceID: str
    ) -> None:
        """Handle JavaScript console messages.

        Parameters
        ----------
        level : int
            The message severity level.
        message : str
            The console message text.
        lineNumber : int
            The source line number.
        sourceID : str
            The source file identifier.
        """
        logger.info(
            f"javaScriptConsoleMessage: {level}, {message}, {lineNumber}, {sourceID}"
        )


class WebPage(QtWidgets.QWidget):
    """Widget that displays a web page in an embedded browser view.

    Parameters
    ----------
    element : Any
        The GUI element descriptor with URL, position, and parent info.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)

        self.element = element

        view = self.view = QtWebEngineWidgets.QWebEngineView(element.parent.widget)

        self.set_geometry()

        page = WebEnginePage(view)
        view.setPage(page)

        if isinstance(self.element.url, str):
            url = self.element.url
        else:
            url = self.element.getvar(element.url.variable_group, element.url.variable)
        url = url.replace("\\", "/")
        view.load(QtCore.QUrl(url))

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reload)
        self.timer.setSingleShot(True)
        self.timer.start(500)

    def set(self) -> None:
        """Update widget state (currently a no-op)."""
        pass

    def set_geometry(self) -> None:
        """Set widget position and size from the element descriptor."""
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.view.setGeometry(x0, y0, wdt, hgt)

    def reload(self) -> None:
        """Reload the web page from the current URL."""
        if isinstance(self.element.url, str):
            url = self.element.url
        else:
            url = self.element.getvar(
                self.element.url.variable_group, self.element.url.variable
            )
        url = url.replace("\\", "/")
        self.view.load(QtCore.QUrl(url))

    def set_url(self, url: str) -> None:
        """Navigate to a new URL.

        Parameters
        ----------
        url : str
            The URL to load (backslashes are converted to forward slashes).
        """
        self.element.url = url.replace("\\", "/")
        self.view.load(QtCore.QUrl(self.element.url))

    def take_screenshot(self, output_file: str) -> None:
        """Save a screenshot of the web page to a file.

        Parameters
        ----------
        output_file : str
            The output file path for the PNG screenshot.
        """
        self.view.grab().save(output_file, b"PNG")
