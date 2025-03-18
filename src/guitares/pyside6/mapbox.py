from PySide6 import QtWebEngineWidgets, QtWebEngineCore, QtCore, QtWidgets, QtWebChannel

import json
from geopandas import GeoDataFrame
from pandas import DataFrame
from pyproj import CRS, Transformer
import os
import requests

from guitares.map.layer import Layer, list_layers, find_layer_by_id

def map_styles():
    available_map_styles = []
    available_map_styles.append({"id": "streets-v12", "name": "Streets"})
    available_map_styles.append({"id": "light-v11", "name": "Light"})
    available_map_styles.append({"id": "dark-v11", "name": "Dark"})
    available_map_styles.append({"id": "satellite-v9", "name": "Satellite"})
    available_map_styles.append({"id": "satellite-streets-v12", "name": "Satellite Streets"})
    return available_map_styles


class WebEnginePage(QtWebEngineCore.QWebEnginePage):
    def __init__(self, view, print_messages):
        super().__init__(view)
        self.print_messages = print_messages

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if self.print_messages:
            print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)


class MapBox(QtWidgets.QWidget):
    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.gui = element.gui
        self.element = element
        self.nr_load_attempts = 0
        self.nr_ready_attempts = 0

        self.crs = CRS(4326)
        self.callback_module = element.module
        self.layer = {}
        self.map_extent = None
        self.map_center = None
        self.map_moved = None
        self.point_clicked_callback = None
        self.zoom = None

        self.url = "http://localhost:" + str(self.gui.server_port)

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
            icon_list_string = icon_list_string + "'/icons/" + icon_file + "',"
        icon_list_string = "[" + icon_list_string + "]"    

        file_name = os.path.join(self.gui.server_path, "js", "defaults.js")
        with open(file_name, "w") as f:
            f.write("var default_style = '" + map_style + "';\n")
            f.write("var default_center = [" + str(element.map_center[0]) + "," + str(element.map_center[1]) + "]\n")
            f.write("var default_zoom = " + str(element.map_zoom) + ";\n")
            f.write("var default_projection = '" + element.map_projection + "';\n")
            if offline:
                f.write("var offline = true;\n")
            else:
                f.write("var offline = false;\n")
            f.write("var iconUrls = " + icon_list_string + ";\n")

        self.webchannel_ok = False
        self.ready = False

        self.server_path = self.gui.server_path

        self.setGeometry(
            0, 0, -1, -1
        )  # this is necessary because otherwise an invisible widget sits over the top left hand side of the screen and block the menu

        self.view = QtWebEngineWidgets.QWebEngineView(element.parent.widget)
        self.view.setPage(WebEnginePage(self.view, self.gui.js_messages))
        self.view.page().settings().setAttribute(QtWebEngineCore.QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        self.view.page().settings().setAttribute(QtWebEngineCore.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

        self.channel = QtWebChannel.QWebChannel()
        self.channel.registerObject("MapBox", self)
        self.view.page().setWebChannel(self.channel)

        self.set_geometry()
        self.view.loadFinished.connect(self.load_finished)
        print(f"Setting url to {self.url}")
        self.view.setUrl(QtCore.QUrl(self.url))

    def load_finished(self, message):
        # self.load_finished = True
        # Sending a ping to javascript
        self.timer_ping = QtCore.QTimer()        
        self.timer_ping.timeout.connect(self.ping)
        self.timer_ping.start(1000)
        # Start a ping received timer
        self.timer_pong = QtCore.QTimer()        
        self.timer_pong.timeout.connect(self.pong_received)
        self.timer_pong.start(1500)

    def ping(self):
        # Sending a ping to javascript
        self.timer_ping.stop()
        self.runjs("/js/main.js", "ping", arglist=["ping"])

    def pong_received(self):
        self.timer_pong.stop()
        if self.webchannel_ok:
            # Tell JS to import Mapbox
            self.runjs("/js/main.js", "importMapbox", arglist=[])
        else:
            # Reload
            self.view.load(QtCore.QUrl(self.url))    

    def set(self):
        pass

    def set_geometry(self):
        x0, y0, wdt, hgt = self.element.get_position()
        self.view.setGeometry(x0, y0, wdt, hgt)

    def take_screenshot(self, output_file):
        self.view.grab().save(output_file, b"PNG")

    @QtCore.Slot(str)
    def pong(self, message):
        # Python heard a pong!
        self.webchannel_ok = True
        # self.runjs("/js/main.js", "importMapbox", arglist=[])

    @QtCore.Slot(str)
    def mapboxImported(self, message):
        self.runjs("/js/main.js", "addMap", arglist=[])

    @QtCore.Slot(str)
    def mapReady(self, coords):
        coords = json.loads(coords)
        self.ready = True
        self.map_extent = coords
        if hasattr(self.callback_module, "map_ready"):
            self.callback_module.map_ready(self)
        # Set dependencies now
        self.element.set_dependencies()

    @QtCore.Slot(str)
    def layerStyleSet(self, coords):
        self.redraw_layers()

    @QtCore.Slot(str)
    def layerAdded(self, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        layer.layer_added()

    @QtCore.Slot(str)
    def mouseMoved(self, coords):
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
    def mapMoved(self, coords):
        coords = json.loads(coords)
        self.map_extent = coords[0:2]
        self.map_center = coords[2:5]
        self.zoom = coords[4]
        # Loop through layers to update each
        layers = list_layers(self.layer)
        for layer in layers:
            layer.update()
        if hasattr(self.callback_module, "map_moved"):
            self.callback_module.map_moved(coords, self)

    @QtCore.Slot(str)
    def pointClicked(self, coords):
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
    def getMapExtent(self, coords):
        coords = json.loads(coords)
        self.map_extent = coords

    @QtCore.Slot(str)
    def getMapCenter(self, coords):
        coords = json.loads(coords)
        self.map_center = coords

    @QtCore.Slot(str, str)
    def featureClicked(self, layer_id, feature_props):
        # Find layer by ID
        layer = find_layer_by_id(layer_id, self.layer)
        if hasattr(layer, "select"):
            if layer.select:
                layer.select(json.loads(feature_props), self)

    @QtCore.Slot(str, str, str)
    def featureDrawn(self, feature_collection, feature_id, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_drawn(json.loads(feature_collection), feature_id)

    @QtCore.Slot(str, str, str)
    def featureModified(self, feature_collection, feature_id, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_modified(json.loads(feature_collection), feature_id)

    @QtCore.Slot(str, str, str)
    def featureSelected(self, feature_collection, feature_id, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_selected(json.loads(feature_collection), feature_id)

    @QtCore.Slot(str)
    def featureDeselected(self, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        if layer:
            layer.feature_deselected()

    @QtCore.Slot(str, str, str)
    def featureAdded(self, feature_collection, feature_id, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_added(json.loads(feature_collection), feature_id)

    def get_extent(self):
        js_string = "import('/js/main.js').then(module => {module.getExtent()});"
        self.view.page().runJavaScript(js_string)

    def get_center(self):
        js_string = "import('/js/main.js').then(module => {module.getCenter()});"
        self.view.page().runJavaScript(js_string)

    def click_point(self, callback):
        self.point_clicked_callback = callback
        self.runjs("/js/main.js", "clickPoint")

    def set_center(self, lon, lat):
        self.runjs("/js/main.js", "setCenter", arglist=[lon, lat])

    def set_zoom(self, zoom):
        self.runjs("/js/main.js", "setZoom", arglist=[zoom])

    def fit_bounds(self, lon1, lat1, lon2, lat2, crs=None):
        if crs is not None:
            if not crs.is_geographic:
                # Convert to lat/lon
                transformer = Transformer.from_crs(crs, 4326, always_xy=True)
                lon1, lat1 = transformer.transform(lon1, lat1)
                lon2, lat2 = transformer.transform(lon2, lat2)
        self.runjs("/js/main.js", "fitBounds", arglist=[lon1, lat1, lon2, lat2])

    def jump_to(self, lon, lat, zoom):
        self.runjs("/js/main.js", "jumpTo", arglist=[lon, lat, zoom])

    def fly_to(self, lon, lat, zoom):
        self.runjs("/js/main.js", "flyTo", arglist=[lon, lat, zoom])

    def set_projection(self, projection):
        self.runjs("/js/main.js", "setProjection", arglist=[projection])

    def set_layer_style(self, style):
        self.runjs("/js/main.js", "setLayerStyle", arglist=[style])

    def set_terrain(self, true_or_false, exaggeration):
        self.runjs("/js/main.js", "setTerrain", arglist=[true_or_false, exaggeration])

    def set_mouse_default(self):
        self.runjs("/js/main.js", "setMouseDefault", arglist=[])
        self.runjs("/js/draw_layer.js", "setMouseDefault", arglist=[])

    def close_popup(self):
        self.runjs("/js/main.js", "closePopup")

    def add_layer(self, layer_id):
        # Adds a container layer
        if layer_id not in self.layer:
            self.layer[layer_id] = Layer(self, layer_id, layer_id)
            self.layer[layer_id].map_id = layer_id
        else:
            print("Layer " + layer_id + " already exists.")
        return self.layer[layer_id]

    def list_layers(self):
        # Return a list with all layers
        return list_layers(self.layer)

    def redraw_layers(self):
        # Redraw all layers (after map style has changed)
        # First clear the layer list in the draw_layer.js file
        self.runjs(
            "/js/draw_layer.js",
            "clearLayerList"
        )
        layers = self.list_layers()
        for layer in layers:
            layer.redraw()

    def compare(self):
        self.runjs("/js/main.js", "compare", arglist=[])

    def runjs(self, module, function, arglist=None):
        if not arglist:
            arglist = []
        string = "import('" + self.url + module + "').then(module => {module." + function + "("
        # string = "import(" + module + "').then(module => {module." + function + "("
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
                string = string + json.dumps(arg).replace('"',"'")
            elif isinstance(arg, list):
                string = string + json.dumps(arg).replace('"',"'")
            elif isinstance(arg, tuple):
                string = string + json.dumps(arg).replace('"',"'")
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
                string = string + "'" + arg + "'"
            if iarg < len(arglist) - 1:
                string = string + ","
        string = string + ")});"
        # print(string)
        self.view.page().runJavaScript(string)
