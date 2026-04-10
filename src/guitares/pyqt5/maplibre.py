"""PyQt5 MapLibre GL JS map widget with WebChannel communication."""

import json
import os
import sys
from typing import Any, Optional

import requests
from geopandas import GeoDataFrame
from pandas import DataFrame
from pyproj import CRS, Transformer
from PyQt5 import QtCore, QtWebChannel, QtWebEngineWidgets

from guitares.map.layer import Layer, find_layer_by_id, list_layers


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    """Custom web engine page that optionally prints JS console messages.

    Parameters
    ----------
    view : QtWebEngineWidgets.QWebEngineView
        The parent web engine view.
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
        if self.print_messages:
            print(f"[JS] {message} (line {lineNumber}, source: {sourceID})")
            sys.stdout.flush()

    def javaScriptAlert(self, security_origin: Any, msg: str) -> None:
        """Suppress JavaScript alert dialogs.

        Parameters
        ----------
        security_origin : Any
            The security origin of the page.
        msg : str
            The alert message.
        """
        pass

    def javaScriptConfirm(self, security_origin: Any, msg: str) -> bool:
        """Suppress JavaScript confirm dialogs.

        Parameters
        ----------
        security_origin : Any
            The security origin of the page.
        msg : str
            The confirm message.

        Returns
        -------
        bool
            Always returns False.
        """
        return False

    def javaScriptPrompt(self, security_origin: Any, msg: str, default: str) -> str:
        """Suppress JavaScript prompt dialogs.

        Parameters
        ----------
        security_origin : Any
            The security origin of the page.
        msg : str
            The prompt message.
        default : str
            The default value.

        Returns
        -------
        str
            Always returns an empty string.
        """
        return ""


class MapLibre(QtCore.QObject):
    """MapLibre GL JS map widget embedded in a PyQt5 QWebEngineView.

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
        self.nr_load_attempts = 0
        self.nr_ready_attempts = 0

        self.crs = CRS(4326)
        self.callback_module = element.module
        self.layer: dict[str, Layer] = {}
        self.map_extent: Optional[list[Any]] = None
        self.map_center: Optional[list[Any]] = None
        self.map_moved: Optional[Any] = None
        self.point_clicked_callback: Optional[Any] = None
        self.zoom: Optional[float] = None

        self.url = f"http://localhost:{self.gui.server_port}"

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
        icon_list_string = ",".join(f"'/icons/{f}'" for f in icon_files)
        icon_list_string = f"[{icon_list_string}]"

        file_name = os.path.join(self.gui.server_path, "js", "defaults.js")
        with open(file_name, "w") as f:
            f.write(f"window.default_style = '{map_style}';\n")
            f.write(
                f"window.default_center = [{element.map_center[0]},{element.map_center[1]}]\n"
            )
            f.write(f"window.default_zoom = {element.map_zoom};\n")
            f.write(f"window.default_projection = '{element.map_projection}';\n")
            f.write(f"window.iconUrls = {icon_list_string};\n")
            if offline:
                f.write("window.offline = true;\n")
            else:
                f.write("window.offline = false;\n")

            # Mapbox token (if available)
            mapbox_token = getattr(element, "mapbox_token", None)
            if not mapbox_token:
                token_file = os.path.join(self.gui.server_path, "mapbox_token.js")
                if os.path.exists(token_file):
                    with open(token_file) as tf:
                        content = tf.read()
                        if "'" in content:
                            mapbox_token = content.split("'")[1]
            if mapbox_token:
                f.write(f"window.mapboxToken = '{mapbox_token}';\n")
            else:
                f.write("window.mapboxToken = null;\n")

            # Terrain sources (optional, set by application)
            terrain_sources = getattr(element, "terrain_sources", None)
            if terrain_sources:
                f.write(f"window.terrainSources = {json.dumps(terrain_sources)};\n")
            else:
                f.write("window.terrainSources = null;\n")

        self.webchannel_ok = False
        self.ready = False

        self.server_path = self.gui.server_path

        self.view = QtWebEngineWidgets.QWebEngineView(element.parent.widget)
        self.view.setPage(WebEnginePage(self.view, self.gui.js_messages))

        self.channel = QtWebChannel.QWebChannel()
        self.channel.registerObject("MapLibre", self)
        self.view.page().setWebChannel(self.channel)

        self.set_geometry()
        self.view.loadFinished.connect(self.load_finished)

        print("Loading map ...")
        self.view.setUrl(QtCore.QUrl(self.url))

    def load_finished(self, message: bool) -> None:
        """Handle page load completion by starting the ping timer.

        Parameters
        ----------
        message : bool
            Whether the page loaded successfully.
        """
        self.timer_ping = QtCore.QTimer()
        self.timer_ping.timeout.connect(self.ping)
        self.timer_ping.start(1000)

    def ping(self) -> None:
        """Send a ping to JavaScript to verify WebChannel connectivity."""
        self.runjs("/js/main.js", "ping", arglist=["ping"])

    def set(self) -> None:
        """Update widget state (currently a no-op)."""
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
        """Set the web view position and size from the element descriptor."""
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
    def pong(self, message: str) -> None:
        """Receive pong from JavaScript, then add the map.

        Parameters
        ----------
        message : str
            The pong message.
        """
        self.timer_ping.stop()
        self.runjs("/js/main.js", "addMap", arglist=[])

    @QtCore.pyqtSlot(str)
    def mapReady(self, coords: str) -> None:
        """Handle map ready event after initialization.

        Parameters
        ----------
        coords : str
            JSON string with the initial map extent.
        """
        coords = json.loads(coords)
        self.ready = True
        self.map_extent = coords
        if hasattr(self.callback_module, "map_ready"):
            self.callback_module.map_ready(self)
        self.element.set_dependencies()

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
    def layerAdded(self, layer_id: str) -> None:
        """Handle layer added notification from JavaScript.

        Parameters
        ----------
        layer_id : str
            The ID of the added layer.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        layer.layer_added()

    @QtCore.pyqtSlot(str)
    def mouseMoved(self, coords: str) -> None:
        """Handle mouse move events, transforming coordinates to the local CRS.

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
            self.callback_module.map_moved(coords, self)

    @QtCore.pyqtSlot(str)
    def pointClicked(self, coords: str) -> None:
        """Handle point click events, transforming to the local CRS.

        Parameters
        ----------
        coords : str
            JSON string with lng/lat coordinates.
        """
        coords = json.loads(coords)
        if self.crs.to_epsg() != 4326:
            transformer = Transformer.from_crs(4326, self.crs, always_xy=True)
            x, y = transformer.transform(coords["lng"], coords["lat"])
        else:
            x = coords["lng"]
            y = coords["lat"]
        if self.point_clicked_callback:
            self.point_clicked_callback(x, y)

    @QtCore.pyqtSlot(str)
    def getMapExtent(self, coords: str) -> None:
        """Store the current map extent.

        Parameters
        ----------
        coords : str
            JSON string with the map extent.
        """
        coords = json.loads(coords)
        self.map_extent = coords

    @QtCore.pyqtSlot(str)
    def getMapCenter(self, coords: str) -> None:
        """Store the current map center.

        Parameters
        ----------
        coords : str
            JSON string with the map center.
        """
        coords = json.loads(coords)
        self.map_center = coords

    @QtCore.pyqtSlot(str, str)
    def featureClicked(self, layer_id: str, feature_props: str) -> None:
        """Handle feature click events on a map layer.

        Parameters
        ----------
        layer_id : str
            The ID of the clicked layer.
        feature_props : str
            JSON string with the feature properties.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        if hasattr(layer, "select"):
            if layer.select:
                layer.select(json.loads(feature_props), self)

    @QtCore.pyqtSlot(str, str, str)
    def featureDrawn(
        self, feature_collection: str, feature_id: str, layer_id: str
    ) -> None:
        """Handle feature drawn events from the drawing tool.

        Parameters
        ----------
        feature_collection : str
            JSON string with the GeoJSON feature collection.
        feature_id : str
            The ID of the drawn feature.
        layer_id : str
            The ID of the target layer.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_drawn(json.loads(feature_collection), feature_id)

    @QtCore.pyqtSlot(str, str, str)
    def featureModified(
        self, feature_collection: str, feature_id: str, layer_id: str
    ) -> None:
        """Handle feature modified events.

        Parameters
        ----------
        feature_collection : str
            JSON string with the updated feature collection.
        feature_id : str
            The ID of the modified feature.
        layer_id : str
            The ID of the target layer.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_modified(json.loads(feature_collection), feature_id)

    @QtCore.pyqtSlot(str, str, str)
    def featureSelected(
        self, feature_collection: str, feature_id: str, layer_id: str
    ) -> None:
        """Handle feature selected events.

        Parameters
        ----------
        feature_collection : str
            JSON string with the selected feature collection.
        feature_id : str
            The ID of the selected feature.
        layer_id : str
            The ID of the target layer.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_selected(json.loads(feature_collection), feature_id)

    @QtCore.pyqtSlot(str)
    def featureDeselected(self, layer_id: str) -> None:
        """Handle feature deselected events.

        Parameters
        ----------
        layer_id : str
            The ID of the target layer.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        if layer:
            layer.feature_deselected()

    @QtCore.pyqtSlot(str, str, str)
    def featureAdded(
        self, feature_collection: str, feature_id: str, layer_id: str
    ) -> None:
        """Handle feature added events.

        Parameters
        ----------
        feature_collection : str
            JSON string with the feature collection.
        feature_id : str
            The ID of the added feature.
        layer_id : str
            The ID of the target layer.
        """
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_added(json.loads(feature_collection), feature_id)

    def get_extent(self) -> None:
        """Request the current map extent from JavaScript."""
        js_string = "import('/js/main.js').then(module => {module.getExtent()});"
        self.view.page().runJavaScript(js_string)

    def get_center(self) -> None:
        """Request the current map center from JavaScript."""
        js_string = "import('/js/main.js').then(module => {module.getCenter()});"
        self.view.page().runJavaScript(js_string)

    def click_point(self, callback: Any) -> None:
        """Enable point-click mode and register a callback.

        Parameters
        ----------
        callback : Any
            Function to call with (x, y) when a point is clicked.
        """
        self.point_clicked_callback = callback
        self.runjs("/js/main.js", "clickPoint")

    def set_center(self, lon: float, lat: float) -> None:
        """Set the map center.

        Parameters
        ----------
        lon : float
            Longitude.
        lat : float
            Latitude.
        """
        self.runjs("/js/main.js", "setCenter", arglist=[lon, lat])

    def set_zoom(self, zoom: float) -> None:
        """Set the map zoom level.

        Parameters
        ----------
        zoom : float
            The zoom level.
        """
        self.runjs("/js/main.js", "setZoom", arglist=[zoom])

    def fit_bounds(
        self,
        lon1: float,
        lat1: float,
        lon2: float,
        lat2: float,
        crs: Optional[CRS] = None,
    ) -> None:
        """Fit the map to the given bounding box, with optional CRS transform.

        Parameters
        ----------
        lon1 : float
            Southwest x-coordinate (or longitude).
        lat1 : float
            Southwest y-coordinate (or latitude).
        lon2 : float
            Northeast x-coordinate (or longitude).
        lat2 : float
            Northeast y-coordinate (or latitude).
        crs : CRS, optional
            If provided and non-geographic, coordinates are transformed to WGS84.
        """
        if crs is not None:
            if not crs.is_geographic:
                transformer = Transformer.from_crs(crs, 4326, always_xy=True)
                lon1, lat1 = transformer.transform(lon1, lat1)
                lon2, lat2 = transformer.transform(lon2, lat2)
        self.runjs("/js/main.js", "fitBounds", arglist=[lon1, lat1, lon2, lat2])

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
        self.runjs("/js/main.js", "jumpTo", arglist=[lon, lat, zoom])

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
        self.runjs("/js/main.js", "flyTo", arglist=[lon, lat, zoom])

    def set_projection(self, projection: str) -> None:
        """Set the map projection.

        Parameters
        ----------
        projection : str
            The projection name.
        """
        self.runjs("/js/main.js", "setProjection", arglist=[projection])

    def set_layer_style(self, style: str) -> None:
        """Set the base map layer style.

        Parameters
        ----------
        style : str
            The map style URL or name.
        """
        self.runjs("/js/main.js", "setLayerStyle", arglist=[style])

    def set_terrain(self, true_or_false: bool, exaggeration: float) -> None:
        """Enable or disable 3D terrain.

        Parameters
        ----------
        true_or_false : bool
            Whether to enable terrain.
        exaggeration : float
            The terrain exaggeration factor.
        """
        self.runjs("/js/main.js", "setTerrain", arglist=[true_or_false, exaggeration])

    def set_mouse_default(self) -> None:
        """Reset the mouse cursor to default mode."""
        self.runjs("/js/main.js", "setMouseDefault", arglist=[])
        self.runjs("/js/draw_layer.js", "setMouseDefault", arglist=[])

    def close_popup(self) -> None:
        """Close any open map popup."""
        self.runjs("/js/main.js", "closePopup")

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
            print(f"Layer {layer_id} already exists.")
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
        self.runjs("/js/draw_layer.js", "clearLayerList")
        layers = self.list_layers()
        for layer in layers:
            layer.redraw()

    def compare(self) -> None:
        """Enable map comparison mode."""
        self.runjs("/js/main.js", "compare", arglist=[])

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
        string = f"import('{self.url}{module}').then(module => {{module.{function}("
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
            elif isinstance(arg, tuple):
                string += json.dumps(arg).replace('"', "'")
            elif isinstance(arg, GeoDataFrame):
                if len(arg) == 0:
                    string += "{}"
                else:
                    # Need to remove timeseries from geodataframe
                    for columnName, columnData in arg.items():
                        if isinstance(columnData.iloc[0], DataFrame):
                            arg = arg.drop([columnName], axis=1)
                    string += arg.to_json()
            elif arg is None:
                string += "null"
            else:
                string += f"'{arg}'"
            if iarg < len(arglist) - 1:
                string += ","
        string += ")});"
        self.view.page().runJavaScript(string)
