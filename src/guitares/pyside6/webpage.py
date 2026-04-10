"""PySide6 web page widget wrapper using QWebEngineView."""

from typing import Any

from PySide6 import QtCore, QtWebEngineCore, QtWebEngineWidgets, QtWidgets


class WebEnginePage(QtWebEngineCore.QWebEnginePage):
    """Custom web engine page that optionally prints JavaScript console messages.

    Parameters
    ----------
    view : QtWebEngineWidgets.QWebEngineView
        The parent web view.
    print_messages : bool
        Whether to print JavaScript console messages to stdout.
    """

    def __init__(
        self, view: QtWebEngineWidgets.QWebEngineView, print_messages: bool
    ) -> None:
        super().__init__(view)
        self.print_messages = print_messages

    def javaScriptConsoleMessage(
        self, level: int, message: str, lineNumber: int, sourceID: str
    ) -> None:
        """Print JavaScript console messages if enabled.

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
        # Suppress JS console messages from documentation panels
        pass


class WebPage(QtWidgets.QWidget):
    """Widget that displays a web page using QWebEngineView.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this web page.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)

        self.element = element

        view = self.view = QtWebEngineWidgets.QWebEngineView(element.parent.widget)

        self.set_geometry()

        page = WebEnginePage(view, element.gui.js_messages)
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
        """Update the web page (currently a no-op)."""
        pass

    def set_geometry(self) -> None:
        """Position and size the web view."""
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
            The new URL to load.
        """
        self.element.url = url.replace("\\", "/")
        self.view.load(QtCore.QUrl(self.element.url))

    def take_screenshot(self, output_file: str) -> None:
        """Save the current web view content as a PNG screenshot.

        Parameters
        ----------
        output_file : str
            The output file path.
        """
        self.view.grab().save(output_file, b"PNG")
