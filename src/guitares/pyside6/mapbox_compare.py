"""PySide6 Mapbox GL JS compare (side-by-side) map widget for Guitares."""

import json
import os
from typing import Any, Callable, Dict, List, Optional

from geopandas import GeoDataFrame
from PySide6 import QtCore, QtWebChannel, QtWebEngineCore, QtWebEngineWidgets, QtWidgets

from guitares.map.layer import Layer, list_layers


class WebEnginePage(QtWebEngineCore.QWebEnginePage):
    """Custom web engine page that optionally prints JavaScript console messages.

    Parameters
    ----------
    view : QtWebEngineWidgets.QWebEngineView
        The parent web view.
    print_messages : bool
        Whether to print JS console messages to stdout.
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
        if self.print_messages:
            print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)


class MapBoxCompare(QtWidgets.QWidget):
    """Side-by-side Mapbox map comparison widget.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this compare map widget.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)

        self.available_map_styles: List[Dict[str, str]] = []
        self.available_map_styles.append({"id": "streets-v12", "name": "Streets"})
        self.available_map_styles.append({"id": "light-v11", "name": "Light"})
        self.available_map_styles.append({"id": "dark-v11", "name": "Dark"})
        self.available_map_styles.append({"id": "satellite-v9", "name": "Satellite"})
        self.available_map_styles.append(
            {"id": "satellite-streets-v12", "name": "Satellite Streets"}
        )

        self.gui = element.gui
        self.element = element

        # Check if element_map_style is in available_map_styles
        if element.map_style not in [
            style["id"] for style in self.available_map_styles
        ]:
            # If not, set to default
            element.map_style = "light-v11"
        # Check if element.map_style starts with "mapbox://styles/"
        if not element.map_style.startswith("mapbox://styles/"):
            # If not, add it
            element.map_style = f"mapbox://styles/mapbox/{element.map_style}"

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
        self.url: str = url

        self.ready: bool = False
        self.ready_a: bool = False
        self.ready_b: bool = False

        self.server_path: str = self.gui.server_path

        self.setGeometry(
            0, 0, -1, -1
        )  # this is necessary because otherwise an invisible widget sits over the top left hand side of the screen and block the menu

        view = self.view = QtWebEngineWidgets.QWebEngineView(element.parent.widget)
        channel = self.channel = QtWebChannel.QWebChannel()
        view.page().profile().clearHttpCache()

        self.set_geometry()

        page = WebEnginePage(view, self.gui.js_messages)
        view.setPage(page)
        view.page().setWebChannel(channel)

        channel.registerObject("MapBoxCompare", self)

        print(f"URL: {url}")

        view.load(QtCore.QUrl(url))

        self.callback_module = element.module

        self.layer: Dict[str, Layer] = {}
        self.map_extent: Optional[Any] = None
        self.map_moved: Optional[Any] = None
        self.point_clicked_callback: Optional[Callable] = None
        self.zoom: Optional[float] = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reload)
        self.timer.setSingleShot(True)
        self.timer.start(1000)

    def reload(self) -> None:
        """Reload the compare page and re-register the WebChannel."""
        print("Reloading ...")
        self.view.page().setWebChannel(self.channel)
        self.channel.registerObject("MapBoxCompare", self)
        self.view.load(QtCore.QUrl(self.url))

    def set(self) -> None:
        """Update the map widget (currently a no-op)."""
        pass

    def set_geometry(self) -> None:
        """Position and size the map view."""
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.view.setGeometry(x0, y0, wdt, hgt)

    def take_screenshot(self, output_file: str) -> None:
        """Save the map as a PNG screenshot.

        Parameters
        ----------
        output_file : str
            The output file path.
        """
        self.view.grab().save(output_file, b"PNG")

    @QtCore.Slot(str)
    def mapReady(self, inpstr: str) -> None:
        """Handle map ready event from JavaScript for each side.

        Parameters
        ----------
        inpstr : str
            JSON string with extent and side identifier ("a" or "b").
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

    @QtCore.Slot(str)
    def layerStyleSet(self, coords: str) -> None:
        """Redraw layers after the map style has changed.

        Parameters
        ----------
        coords : str
            Unused.
        """
        self.redraw_layers()

    @QtCore.Slot(str)
    def mapMoved(self, coords: str) -> None:
        """Handle map move/zoom events and update layers.

        Parameters
        ----------
        coords : str
            JSON string with extent, center, and zoom.
        """
        coords = json.loads(coords)
        self.map_extent = coords[0:2]
        self.map_center = coords[2:5]
        self.zoom = coords[4]
        # Loop through layers to update each
        layers = list_layers(self.layer)
        for layer in layers:
            layer.update()
        if hasattr(self.callback_module, "map_moved"):
            self.callback_module.map_moved(coords)

    def jump_to(self, lon: float, lat: float, zoom: float) -> None:
        """Jump to a map position without animation.

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
        """Fly to a map position with animation.

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
        """Set the map base layer style.

        Parameters
        ----------
        style : str
            The style identifier.
        """
        self.runjs("/js/compare.js", "setLayerStyle", arglist=[style])

    def set_slider(self, npix: int) -> None:
        """Set the compare slider position.

        Parameters
        ----------
        npix : int
            Slider position in pixels.
        """
        self.runjs("/js/compare.js", "setSlider", arglist=[npix])

    def add_layer(self, layer_id: str) -> Layer:
        """Add a container layer to the map.

        Parameters
        ----------
        layer_id : str
            The layer identifier.

        Returns
        -------
        Layer
            The created or existing layer object.
        """
        if layer_id not in self.layer:
            self.layer[layer_id] = Layer(self, layer_id, layer_id)
            self.layer[layer_id].map_id = layer_id
        else:
            print(f"Layer {layer_id} already exists.")
        return self.layer[layer_id]

    def list_layers(self) -> List[Layer]:
        """Return a flat list of all layers.

        Returns
        -------
        List[Layer]
            All layers in the map.
        """
        return list_layers(self.layer)

    def redraw_layers(self) -> None:
        """Redraw all layers (after map style has changed)."""
        layers = self.list_layers()
        for layer in layers:
            layer.redraw()

    def runjs(
        self, module: str, function: str, arglist: Optional[List[Any]] = None
    ) -> None:
        """Execute a JavaScript function via dynamic import.

        Parameters
        ----------
        module : str
            The JS module path.
        function : str
            The function name to call.
        arglist : Optional[List[Any]]
            Arguments to pass to the function.
        """
        if not arglist:
            arglist = []
        string = f"import('{module}').then(module => {{module.{function}("
        for iarg, arg in enumerate(arglist):
            if isinstance(arg, bool):
                if arg:
                    string = string + "true"
                else:
                    string = string + "false"
            elif isinstance(arg, int):
                string = string + str(arg)
            elif isinstance(arg, float):
                string = string + str(arg)
            elif isinstance(arg, dict):
                string = string + json.dumps(arg).replace('"', "'")
            elif isinstance(arg, list):
                string = string + json.dumps(arg).replace('"', "'")
            elif isinstance(arg, GeoDataFrame):
                if len(arg) == 0:
                    string = string + "{}"
                else:
                    string = string + arg.to_json()
            else:
                string = f"{string}'{arg}'"
            if iarg < len(arglist) - 1:
                string = string + ","
        string = string + ")});"
        self.view.page().runJavaScript(string)
