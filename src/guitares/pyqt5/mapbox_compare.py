"""PyQt5 Mapbox GL JS comparison map widget with side-by-side views."""

import json
import logging
import os
from typing import Any, Optional

from geopandas import GeoDataFrame
from PyQt5 import QtCore, QtWebChannel, QtWebEngineWidgets, QtWidgets

from guitares.map.layer import Layer, list_layers

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
            f"javaScriptConsoleMessage: {level} {message} {lineNumber} {sourceID}"
        )


class MapBoxCompare(QtWidgets.QWidget):
    """Side-by-side Mapbox GL JS comparison map widget.

    Parameters
    ----------
    element : Any
        The GUI element descriptor with map style, center, zoom, projection,
        and parent info.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)

        self.gui = element.gui
        self.element = element

        file_name = os.path.join(
            self.gui.server_path, "js", "mapbox_compare_defaults.js"
        )
        with open(file_name, "w") as f:
            f.write(f"var default_compare_style = '{element.map_style}';\n")
            f.write(
                f"var default_compare_center = [{element.map_center[0]},{element.map_center[1]}]\n"
            )
            f.write(f"var default_compare_zoom = {element.map_zoom};\n")
            f.write(f"var default_compare_projection = '{element.map_projection}';\n")

        url = f"http://localhost:{self.gui.server_port}/mapbox_compare.html"
        self.url = url

        self.ready = False
        self.ready_a = False
        self.ready_b = False

        self.server_path = self.gui.server_path

        self.setGeometry(
            0, 0, -1, -1
        )  # this is necessary because otherwise an invisible widget sits over the top left hand side of the screen and block the menu

        view = self.view = QtWebEngineWidgets.QWebEngineView(element.parent.widget)
        channel = self.channel = QtWebChannel.QWebChannel()
        view.page().profile().clearHttpCache()

        self.set_geometry()

        page = WebEnginePage(view)
        view.setPage(page)
        view.page().setWebChannel(channel)

        channel.registerObject("MapBoxCompare", self)

        view.load(QtCore.QUrl(url))

        self.callback_module = element.module

        self.layer: dict[str, Layer] = {}
        self.map_extent: Optional[list[Any]] = None
        self.map_moved: Optional[Any] = None
        self.point_clicked_callback: Optional[Any] = None
        self.zoom: Optional[float] = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reload)
        self.timer.setSingleShot(True)
        self.timer.start(1000)

    def reload(self) -> None:
        """Reload the comparison map page."""
        logger.info("Reloading ...")
        self.view.page().setWebChannel(self.channel)
        self.channel.registerObject("MapBoxCompare", self)
        self.view.load(QtCore.QUrl(self.url))

    def set(self) -> None:
        """Update widget state (currently a no-op)."""
        pass

    def set_geometry(self) -> None:
        """Set the web view position and size from the element descriptor."""
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.view.setGeometry(x0, y0, wdt, hgt)

    def take_screenshot(self, output_file: str) -> None:
        """Save a screenshot of the map to a PNG file.

        Parameters
        ----------
        output_file : str
            The output file path.
        """
        self.view.grab().save(output_file, b"PNG")

    @QtCore.pyqtSlot(str)
    def mapReady(self, inpstr: str) -> None:
        """Handle map ready event for each side (a/b) of the comparison.

        Parameters
        ----------
        inpstr : str
            JSON string with extent and side identifier.
        """
        inp = json.loads(inpstr)
        coords = inp[0:2]
        self.map_extent = coords
        side = inp[2]
        if side == "a":
            self.ready_a = True
        elif side == "b":
            self.ready_b = True
        if self.ready_a and self.ready_b:
            self.ready = True
        if self.ready:
            if hasattr(self.callback_module, "map_ready"):
                self.callback_module.map_ready()

    @QtCore.pyqtSlot(str)
    def layerStyleSet(self, coords: str) -> None:
        """Handle layer style change by redrawing all layers.

        Parameters
        ----------
        coords : str
            Unused parameter from JavaScript callback.
        """
        self.redraw_layers()

    @QtCore.pyqtSlot(str)
    def mapMoved(self, coords: str) -> None:
        """Handle map pan/zoom events and update all layers.

        Parameters
        ----------
        coords : str
            JSON string with extent, center, and zoom data.
        """
        coords = json.loads(coords)
        self.map_extent = coords[0:2]
        self.map_center = coords[2:5]
        self.zoom = coords[4]
        layers = list_layers(self.layer)
        for layer in layers:
            layer.update()
        if hasattr(self.callback_module, "map_moved"):
            self.callback_module.map_moved(coords)

    def jump_to(self, lon: float, lat: float, zoom: float) -> None:
        """Jump to a location without animation.

        Parameters
        ----------
        lon : float
            Longitude.
        lat : float
            Latitude.
        zoom : float
            Zoom level.
        """
        self.runjs("/js/compare.js", "jumpTo", arglist=[lon, lat, zoom])

    def fly_to(self, lon: float, lat: float, zoom: float) -> None:
        """Fly to a location with animation.

        Parameters
        ----------
        lon : float
            Longitude.
        lat : float
            Latitude.
        zoom : float
            Zoom level.
        """
        self.runjs("/js/compare.js", "flyTo", arglist=[lon, lat, zoom])

    def set_layer_style(self, style: str) -> None:
        """Set the base map layer style.

        Parameters
        ----------
        style : str
            The map style URL or name.
        """
        self.runjs("/js/compare.js", "setLayerStyle", arglist=[style])

    def set_slider(self, npix: int) -> None:
        """Set the comparison slider position.

        Parameters
        ----------
        npix : int
            The slider position in pixels.
        """
        self.runjs("/js/compare.js", "setSlider", arglist=[npix])

    def add_layer(self, layer_id: str) -> Layer:
        """Add a container layer to the map.

        Parameters
        ----------
        layer_id : str
            The unique layer identifier.

        Returns
        -------
        Layer
            The created layer object.
        """
        if layer_id not in self.layer:
            self.layer[layer_id] = Layer(self, layer_id, layer_id)
            self.layer[layer_id].map_id = layer_id
        else:
            logger.warning(f"Layer {layer_id} already exists.")
        return self.layer[layer_id]

    def list_layers(self) -> list[Any]:
        """Return a flat list of all layers.

        Returns
        -------
        list[Any]
            All layer objects.
        """
        return list_layers(self.layer)

    def redraw_layers(self) -> None:
        """Redraw all layers after a map style change."""
        layers = self.list_layers()
        for layer in layers:
            layer.redraw()

    def runjs(
        self, module: str, function: str, arglist: Optional[list[Any]] = None
    ) -> None:
        """Execute a JavaScript function via dynamic import.

        Parameters
        ----------
        module : str
            The JavaScript module path.
        function : str
            The function name to call.
        arglist : list[Any], optional
            Arguments to pass to the function.
        """
        if not arglist:
            arglist = []
        string = f"import('{module}').then(module => {{module.{function}("
        for iarg, arg in enumerate(arglist):
            if isinstance(arg, bool):
                string += "true" if arg else "false"
            elif isinstance(arg, int):
                string += str(arg)
            elif isinstance(arg, float):
                string += str(arg)
            elif isinstance(arg, dict):
                string += json.dumps(arg).replace('"', "'")
            elif isinstance(arg, list):
                string += json.dumps(arg).replace('"', "'")
            elif isinstance(arg, GeoDataFrame):
                if len(arg) == 0:
                    string += "{}"
                else:
                    string += arg.to_json()
            else:
                string += f"'{arg}'"
            if iarg < len(arglist) - 1:
                string += ","
        string += ")});"
        self.view.page().runJavaScript(string)
