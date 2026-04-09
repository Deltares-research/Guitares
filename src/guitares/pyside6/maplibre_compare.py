"""PySide6 MapLibre GL JS compare (side-by-side) map widget for Guitares."""

import json
import os
import sys
from collections import deque
from typing import Any, Callable, Deque, Dict, List, Optional

import requests
from geopandas import GeoDataFrame
from pandas import DataFrame
from pyproj import CRS, Transformer
from PySide6 import QtCore, QtWebChannel, QtWebEngineCore, QtWebEngineWidgets

from guitares.map.layer import Layer, find_layer_by_id, list_layers


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
            # Suppress noisy DOMException errors from MapLibre internals
            if "DOMException" in message:
                return
            print(f"[JS] {message} (line {lineNumber}, source: {sourceID})")
            sys.stdout.flush()  # Ensures it appears even if buffering is active

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


class MapLibreCompare(QtCore.QObject):
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
        self.nr_load_attempts: int = 0
        self.nr_ready_attempts: int = 0

        self.crs: CRS = CRS(4326)
        self.callback_module = element.module
        self.layer: Dict[str, Layer] = {}
        self.map_extent: Optional[Any] = None
        self.map_center: Optional[Any] = None
        self.map_moved: Optional[Any] = None
        self.point_clicked_callback: Optional[Callable] = None
        self.zoom: Optional[float] = None

        self.url: str = f"http://localhost:{self.gui.server_port}"

        # Check for internet connection
        try:
            requests.get("http://www.google.com", timeout=5)
        except requests.ConnectionError:
            print("No internet connection available.")
            map_style = "none"
            offline = True
        else:
            print("Internet connection available.")
            map_style = element.map_style
            offline = False

        # List all icon files in the icons folder
        icon_path = os.path.join(self.gui.server_path, "icons")
        icon_files = os.listdir(icon_path)
        icon_files = [f for f in icon_files if f.endswith(".png")]
        icon_list_string = ""
        for icon_file in icon_files:
            icon_list_string = f"{icon_list_string}'/icons/{icon_file}',"
        icon_list_string = f"[{icon_list_string}]"

        file_name = os.path.join(
            self.gui.server_path, "js", "maplibre_compare_defaults.js"
        )
        with open(file_name, "w") as f:
            f.write(f"window.default_compare_style = '{map_style}';\n")
            f.write(
                f"window.default_compare_center = [{element.map_center[0]},{element.map_center[1]}]\n"
            )
            f.write(f"window.default_compare_zoom = {element.map_zoom};\n")
            f.write(f"window.default_compare_projection = '{element.map_projection}';\n")
            f.write(f"window.compareIconUrls = {icon_list_string};\n")
            if offline:
                f.write("window.compare_offline = true;\n")
            else:
                f.write("window.compare_offline = false;\n")

            # Mapbox token (if available)
            mapbox_token = getattr(element, "mapbox_token", None)
            if not mapbox_token:
                # Check for mapbox_token.js written by gui.py
                token_file = os.path.join(self.gui.server_path, "mapbox_token.js")
                if os.path.exists(token_file):
                    with open(token_file) as tf:
                        content = tf.read()
                        # Parse: mapbox_token = 'pk.xxx';
                        if "'" in content:
                            mapbox_token = content.split("'")[1]
            if mapbox_token:
                f.write(f"window.compareMapboxToken = '{mapbox_token}';\n")
            else:
                f.write("window.compareMapboxToken = null;\n")

            # Terrain sources (optional, set by application)
            terrain_sources = getattr(element, "terrain_sources", None)
            if terrain_sources:
                f.write(
                    f"window.compareTerrainSources = {json.dumps(terrain_sources)};\n"
                )
            else:
                f.write("window.compareTerrainSources = null;\n")

        self.ready: bool = False
        self.ready_a: bool = False
        self.ready_b: bool = False

        self.webchannel_ok: bool = False

        self.server_path: str = self.gui.server_path

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

        print("Loading compare map ...")
        self.view.setUrl(QtCore.QUrl(f"{self.url}/maplibre_compare.html"))

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
        # print("Ping!")
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
        # print("Pong received! Adding map compare ...")
        # Add map
        self.runjs("/js/compare.js", "addMap", arglist=[])

    def set(self) -> None:
        """Update the map widget (currently a no-op)."""
        pass

    def setVisible(self, visible: bool) -> None:
        """Show or hide the map view.

        Parameters
        ----------
        visible : bool
            Whether to show the view.
        """
        self.view.setVisible(visible)

    def set_geometry(self) -> None:
        """Position and size the map view."""
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
    def layerAdded(self, layer_id: str) -> None:
        """Notify a layer that it has been added to the map.

        Parameters
        ----------
        layer_id : str
            The layer identifier.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        layer.layer_added()

    @QtCore.Slot(str)
    def mouseMoved(self, coords: str) -> None:
        """Forward mouse move events to the callback module.

        Parameters
        ----------
        coords : str
            JSON string with lng/lat coordinates.
        """
        if hasattr(self.callback_module, "mouse_moved"):
            coords = json.loads(coords)
            lon = coords["lng"]
            lat = coords["lat"]
            if not self.crs.is_geographic:
                transformer = Transformer.from_crs(4326, self.crs, always_xy=True)
                x, y = transformer.transform(lon, lat)
            else:
                x = lon
                y = lat
            self.callback_module.mouse_moved(x, y, lon, lat)

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

    @QtCore.Slot(str)
    def pointClicked(self, coords: str) -> None:
        """Handle point click events on the map.

        Parameters
        ----------
        coords : str
            JSON string with lng/lat of the clicked point.
        """
        coords = json.loads(coords)
        # Transform to local crs
        if self.crs.to_epsg() != 4326:
            transformer = Transformer.from_crs(4326, self.crs, always_xy=True)
            x, y = transformer.transform(coords["lng"], coords["lat"])
        else:
            x = coords["lng"]
            y = coords["lat"]
        if self.point_clicked_callback:
            self.point_clicked_callback(x, y)

    @QtCore.Slot(str)
    def getMapExtent(self, coords: str) -> None:
        """Store the current map extent.

        Parameters
        ----------
        coords : str
            JSON string with the map extent.
        """
        coords = json.loads(coords)
        self.map_extent = coords

    @QtCore.Slot(str)
    def getMapCenter(self, coords: str) -> None:
        """Store the current map center.

        Parameters
        ----------
        coords : str
            JSON string with the map center.
        """
        coords = json.loads(coords)
        self.map_center = coords

    @QtCore.Slot(str, str)
    def featureClicked(self, layer_id: str, feature_props: str) -> None:
        """Forward feature click events to the appropriate layer.

        Parameters
        ----------
        layer_id : str
            The layer identifier.
        feature_props : str
            JSON string with feature properties.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        if hasattr(layer, "select"):
            if layer.select:
                layer.select(json.loads(feature_props), self)

    @QtCore.Slot(str, str, str)
    def featureDrawn(
        self, feature_collection: str, feature_id: str, layer_id: str
    ) -> None:
        """Forward feature draw events to the appropriate layer.

        Parameters
        ----------
        feature_collection : str
            JSON string with the feature collection.
        feature_id : str
            The feature identifier.
        layer_id : str
            The layer identifier.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_drawn(json.loads(feature_collection), feature_id)

    @QtCore.Slot(str, str, str)
    def featureModified(
        self, feature_collection: str, feature_id: str, layer_id: str
    ) -> None:
        """Forward feature modify events to the appropriate layer.

        Parameters
        ----------
        feature_collection : str
            JSON string with the feature collection.
        feature_id : str
            The feature identifier.
        layer_id : str
            The layer identifier.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_modified(json.loads(feature_collection), feature_id)

    @QtCore.Slot(str, str, str)
    def featureSelected(
        self, feature_collection: str, feature_id: str, layer_id: str
    ) -> None:
        """Forward feature select events to the appropriate layer.

        Parameters
        ----------
        feature_collection : str
            JSON string with the feature collection.
        feature_id : str
            The feature identifier.
        layer_id : str
            The layer identifier.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_selected(json.loads(feature_collection), feature_id)

    @QtCore.Slot(str)
    def featureDeselected(self, layer_id: str) -> None:
        """Forward feature deselect events to the appropriate layer.

        Parameters
        ----------
        layer_id : str
            The layer identifier.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        if layer:
            layer.feature_deselected()

    @QtCore.Slot(str, str, str)
    def featureAdded(
        self, feature_collection: str, feature_id: str, layer_id: str
    ) -> None:
        """Forward feature add events to the appropriate layer.

        Parameters
        ----------
        feature_collection : str
            JSON string with the feature collection.
        feature_id : str
            The feature identifier.
        layer_id : str
            The layer identifier.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_added(json.loads(feature_collection), feature_id)

    def get_extent(self) -> None:
        """Request the current map extent from JavaScript."""
        js_string = "import('/js/compare.js').then(module => {module.getExtent()});"
        self.view.page().runJavaScript(js_string)

    def get_center(self) -> None:
        """Request the current map center from JavaScript."""
        js_string = "import('/js/compare.js').then(module => {module.getCenter()});"
        self.view.page().runJavaScript(js_string)

    def click_point(self, callback: Callable) -> None:
        """Enable point-click mode on the map.

        Parameters
        ----------
        callback : Callable
            Function to call with (x, y) when a point is clicked.
        """
        self.point_clicked_callback = callback
        self.runjs("/js/compare.js", "clickPoint")

    def set_center(self, lon: float, lat: float) -> None:
        """Set the map center.

        Parameters
        ----------
        lon : float
            Longitude.
        lat : float
            Latitude.
        """
        self.runjs("/js/compare.js", "setCenter", arglist=[lon, lat])

    def set_zoom(self, zoom: float) -> None:
        """Set the map zoom level.

        Parameters
        ----------
        zoom : float
            The zoom level.
        """
        self.runjs("/js/compare.js", "setZoom", arglist=[zoom])

    def fit_bounds(
        self,
        lon1: float,
        lat1: float,
        lon2: float,
        lat2: float,
        crs: Optional[CRS] = None,
    ) -> None:
        """Fit the map to the given bounding box.

        Parameters
        ----------
        lon1 : float
            Western longitude (or x in local CRS).
        lat1 : float
            Southern latitude (or y in local CRS).
        lon2 : float
            Eastern longitude (or x in local CRS).
        lat2 : float
            Northern latitude (or y in local CRS).
        crs : Optional[CRS]
            If provided, coordinates are transformed from this CRS to WGS84.
        """
        if crs is not None:
            if not crs.is_geographic:
                # Convert to lat/lon
                transformer = Transformer.from_crs(crs, 4326, always_xy=True)
                lon1, lat1 = transformer.transform(lon1, lat1)
                lon2, lat2 = transformer.transform(lon2, lat2)
        self.runjs("/js/compare.js", "fitBounds", arglist=[lon1, lat1, lon2, lat2])

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

    def set_projection(self, projection: str) -> None:
        """Set the map projection.

        Parameters
        ----------
        projection : str
            The projection name.
        """
        self.runjs("/js/compare.js", "setProjection", arglist=[projection])

    def set_terrain(self, true_or_false: bool, exaggeration: float) -> None:
        """Enable or disable 3D terrain.

        Parameters
        ----------
        true_or_false : bool
            Whether to enable terrain.
        exaggeration : float
            The terrain exaggeration factor.
        """
        self.runjs(
            "/js/compare.js", "setTerrain", arglist=[true_or_false, exaggeration]
        )

    def set_mouse_default(self) -> None:
        """Reset the mouse cursor to default mode."""
        self.runjs("/js/compare.js", "setMouseDefault", arglist=[])
        self.runjs("/js/draw_layer.js", "setMouseDefault", arglist=[])

    def close_popup(self) -> None:
        """Close any open popup on the map."""
        self.runjs("/js/compare.js", "closePopup")

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
        # First clear the layer list in the draw_layer.js file
        self.runjs("/js/draw_layer.js", "clearLayerList")
        layers = self.list_layers()
        for layer in layers:
            layer.redraw()

    def runjs(self, module: str, function: str, **kwargs: Any) -> None:
        """Execute a JavaScript function via dynamic import, serialized.

        Supports both positional args (via ``arglist`` keyword) and keyword
        args that are passed as a JS object literal.

        Parameters
        ----------
        module : str
            The JS module path (e.g. "/js/compare.js").
        function : str
            The function name to call.
        **kwargs : Any
            Either ``arglist=[...]`` for positional args, or named kwargs
            for a JS object argument.
        """
        string = f"import('{self.url}{module}').then(module => {{module.{function}("

        if "arglist" in kwargs:
            # "old" way of passing arguments
            arglist = kwargs["arglist"]

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
                        # Need to remove timeseries from geodataframe
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

        elif len(kwargs) > 0:
            # Loop through the kwargs and add them to the arglist

            string = string + "{"

            for key, value in kwargs.items():
                if isinstance(value, bool):
                    if value:
                        argstr = f"{key}: true"
                    else:
                        argstr = f"{key}: false"
                elif isinstance(value, int):
                    argstr = f"{key}: {value}"
                elif isinstance(value, float):
                    argstr = f"{key}: {value}"
                elif isinstance(value, dict):
                    argstr = f"{key}: " + json.dumps(value).replace('"', "'")
                elif isinstance(value, list):
                    argstr = f"{key}: " + json.dumps(value).replace('"', "'")
                elif isinstance(value, tuple):
                    argstr = f"{key}: " + json.dumps(value).replace('"', "'")
                elif isinstance(value, GeoDataFrame):
                    if len(value) == 0:
                        argstr = f"{key}: {{}}"
                    else:
                        # Need to remove timeseries from geodataframe
                        for columnName, columnData in value.items():
                            if isinstance(columnData.iloc[0], DataFrame):
                                value = value.drop([columnName], axis=1)
                        argstr = f"{key}: " + value.to_json()
                elif value is None:
                    argstr = f"{key}: null"
                else:
                    argstr = f"{key}: '{value}'"

                argstr = argstr + ", "

                string = string + argstr

            string = string + "})}); void 0;"

        else:
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
