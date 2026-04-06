"""PySide6 MapLibre GL JS compare (side-by-side) map widget for Guitares."""

import json
import os
import sys
from collections import deque
from typing import Any, Callable, Deque, Dict, List, Optional

from geopandas import GeoDataFrame
from pandas import DataFrame
from PySide6 import QtCore, QtWebChannel, QtWebEngineCore, QtWebEngineWidgets, QtWidgets

from guitares.map.layer import Layer, list_layers


class WebEnginePage(QtWebEngineCore.QWebEnginePage):
    """Custom web engine page with JS console output and suppressed JS dialogs.

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
            print(f"[JS] {message} (line {lineNumber}, source: {sourceID})")
            sys.stdout.flush()

    def javaScriptAlert(self, security_origin: Any, msg: str) -> None:
        """Suppress JavaScript alert() dialogs.

        Parameters
        ----------
        security_origin : Any
            The security origin.
        msg : str
            The alert message.
        """
        pass

    def javaScriptConfirm(self, security_origin: Any, msg: str) -> bool:
        """Suppress JavaScript confirm() dialogs.

        Parameters
        ----------
        security_origin : Any
            The security origin.
        msg : str
            The confirm message.

        Returns
        -------
        bool
            Always False.
        """
        return False

    def javaScriptPrompt(self, security_origin: Any, msg: str, default: str) -> str:
        """Suppress JavaScript prompt() dialogs.

        Parameters
        ----------
        security_origin : Any
            The security origin.
        msg : str
            The prompt message.
        default : str
            The default value.

        Returns
        -------
        str
            Always empty string.
        """
        return ""


class MapLibreCompare(QtWidgets.QWidget):
    """Side-by-side MapLibre map comparison widget with serial JS execution.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this compare map widget.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)

        self._js_queue: Deque[str] = deque()
        self._js_running: bool = False

        self.gui = element.gui
        self.element = element

        self.callback_module = element.module

        file_name = os.path.join(
            self.gui.server_path, "js", "maplibre_compare_defaults.js"
        )
        with open(file_name, "w") as f:
            f.write(f"var default_compare_style = '{element.map_style}';\n")
            f.write(
                f"var default_compare_center = [{element.map_center[0]},{element.map_center[1]}]\n"
            )
            f.write(f"var default_compare_zoom = {element.map_zoom};\n")
            f.write(f"var default_compare_projection = '{element.map_projection}';\n")

        self.url: str = f"http://localhost:{self.gui.server_port}"

        self.ready: bool = False
        self.ready_a: bool = False
        self.ready_b: bool = False

        self.webchannel_ok: bool = False

        self.server_path: str = self.gui.server_path

        self.setGeometry(
            0, 0, -1, -1
        )  # this is necessary because otherwise an invisible widget sits over the top left hand side of the screen and block the menu

        self.view = QtWebEngineWidgets.QWebEngineView(element.parent.widget)
        self.view.setPage(WebEnginePage(self.view, self.gui.js_messages))
        self.view.page().settings().setAttribute(
            QtWebEngineCore.QWebEngineSettings.WebAttribute.WebGLEnabled, True
        )
        self.view.page().settings().setAttribute(
            QtWebEngineCore.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True
        )

        self.channel = QtWebChannel.QWebChannel()
        self.channel.registerObject("MapLibreCompare", self)
        self.view.page().setWebChannel(self.channel)

        self.set_geometry()
        self.view.loadFinished.connect(self.load_finished)
        self.view.setUrl(QtCore.QUrl(f"{self.url}/maplibre_compare.html"))

        self.layer: Dict[str, Layer] = {}
        self.map_extent: Optional[Any] = None
        self.map_moved: Optional[Any] = None
        self.point_clicked_callback: Optional[Callable] = None
        self.zoom: Optional[float] = None

    def load_finished(self, message: bool) -> None:
        """Start ping timer after page load.

        Parameters
        ----------
        message : bool
            Whether the load was successful.
        """
        self.timer_ping = QtCore.QTimer()
        self.timer_ping.timeout.connect(self.ping)
        self.timer_ping.start(1000)

    def ping(self) -> None:
        """Send a ping to JavaScript to verify the WebChannel is working."""
        print("Ping!")
        self.runjs("/js/compare.js", "ping", arglist=["ping"])

    @QtCore.Slot(str)
    def pong(self, message: str) -> None:
        """Receive pong from JavaScript, confirming WebChannel is active.

        Parameters
        ----------
        message : str
            The pong message.
        """
        self.timer_ping.stop()
        print("Pong received! Adding map compare ...")
        # Add map
        self.runjs("/js/compare.js", "addMap", arglist=[])

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
        """Execute a JavaScript function via dynamic import, serialized.

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
        string = f"import('{self.url}{module}').then(module => {{module.{function}("
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
            elif isinstance(arg, tuple):
                string = string + json.dumps(arg).replace('"', "'")
            elif isinstance(arg, GeoDataFrame):
                if len(arg) == 0:
                    string = string + "{}"
                else:
                    for columnName, columnData in arg.items():
                        if isinstance(columnData.iloc[0], DataFrame):
                            arg = arg.drop([columnName], axis=1)
                    string = string + arg.to_json()
            elif arg is None:
                string = string + "null"
            else:
                string = f"{string}'{arg}'"
            if iarg < len(arglist) - 1:
                string = string + ","
        string = string + ")}); void 0;"
        self.run_js_serial(string)

    def run_js_serial(self, code: str) -> None:
        """Queue and execute JavaScript code serially to avoid race conditions.

        Parameters
        ----------
        code : str
            The JavaScript code to execute.
        """
        self._js_queue.append(code)
        if not self._js_running:
            self._run_next()

    def _run_next(self) -> None:
        """Execute the next queued JavaScript snippet."""
        if not self._js_queue:
            self._js_running = False
            return

        self._js_running = True
        code = self._js_queue.popleft()

        self.view.page().runJavaScript(code, lambda _: self._run_next())
