from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets, QtWebChannel
import json
from geopandas import GeoDataFrame
from pandas import DataFrame
from pyproj import CRS, Transformer
import os
from guitares.map.layer import Layer, list_layers, find_layer_by_id

class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
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

        # List all icon files in the icons folder
        icon_path = os.path.join(self.gui.server_path, "icons")
        icon_files = os.listdir(icon_path)
        icon_files = [f for f in icon_files if f.endswith(".png")]
        icon_list_string = ""
        for icon_file in icon_files:
            icon_list_string = icon_list_string + "'/icons/" + icon_file + "',"
        icon_list_string = "[" + icon_list_string + "]"    

        file_name = os.path.join(self.gui.server_path, "js", "mapbox_defaults.js")
        with open(file_name, "w") as f:
            f.write("var default_style = '" + element.map_style + "';\n")
            f.write("var default_center = [" + str(element.map_center[0]) + "," + str(element.map_center[1]) + "]\n")
            f.write("var default_zoom = " + str(element.map_zoom) + ";\n")
            f.write("var default_projection = '" + element.map_projection + "';\n")
            f.write("var iconUrls = " + icon_list_string + ";\n")

        url = "http://localhost:" + str(self.gui.server_port) + "/"
        self.url = url

        self.webchannel_ok = False
        self.ready = False

        self.server_path = self.gui.server_path

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

        channel.registerObject("MapBox", self)

        view.loadFinished.connect(self.load_finished)

        view.load(QtCore.QUrl(url))

        self.crs = CRS(4326)
        self.callback_module = element.module
        self.layer = {}
        self.map_extent = None
        self.map_center = None
        self.map_moved = None
        self.point_clicked_callback = None
        self.zoom = None

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

    @QtCore.pyqtSlot(str)
    def pong(self, message):
        # Python heard a pong!
        self.webchannel_ok = True
        # self.runjs("/js/main.js", "importMapbox", arglist=[])

    @QtCore.pyqtSlot(str)
    def mapboxImported(self, message):
        self.runjs("/js/main.js", "addMap", arglist=[])

    @QtCore.pyqtSlot(str)
    def mapReady(self, coords):
        coords = json.loads(coords)
        self.ready = True
        self.map_extent = coords
        if hasattr(self.callback_module, "map_ready"):
            self.callback_module.map_ready(self)
        # Set dependencies now
        self.element.set_dependencies()

    @QtCore.pyqtSlot(str)
    def layerStyleSet(self, coords):
        self.redraw_layers()

    @QtCore.pyqtSlot(str)
    def layerAdded(self, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        layer.layer_added()

    @QtCore.pyqtSlot(str)
    def mouseMoved(self, coords):
        coords = json.loads(coords)
        self.map_extent = coords
        # # Loop through layers to update each
        # layers = list_layers(self.layer)
        # for layer in layers:
        #     layer.update()
        if hasattr(self.callback_module, "mouse_moved"):
            self.callback_module.mouse_moved(coords)

    @QtCore.pyqtSlot(str)
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

    @QtCore.pyqtSlot(str)
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

    @QtCore.pyqtSlot(str)
    def getMapExtent(self, coords):
        coords = json.loads(coords)
        self.map_extent = coords

    @QtCore.pyqtSlot(str)
    def getMapCenter(self, coords):
        coords = json.loads(coords)
        self.map_center = coords

    @QtCore.pyqtSlot(str, str)
    def featureClicked(self, layer_id, feature_props):
        # Find layer by ID
        layer = find_layer_by_id(layer_id, self.layer)
        if hasattr(layer, "select"):
            if layer.select:
                layer.select(json.loads(feature_props), self)

    @QtCore.pyqtSlot(str, str, str)
    def featureDrawn(self, feature_collection, feature_id, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_drawn(json.loads(feature_collection), feature_id)

    @QtCore.pyqtSlot(str, str, str)
    def featureModified(self, feature_collection, feature_id, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_modified(json.loads(feature_collection), feature_id)

    @QtCore.pyqtSlot(str, str, str)
    def featureSelected(self, feature_collection, feature_id, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        layer.feature_selected(json.loads(feature_collection), feature_id)

    @QtCore.pyqtSlot(str)
    def featureDeselected(self, layer_id):
        layer = find_layer_by_id(layer_id, self.layer)
        if layer:
            layer.feature_deselected()

    @QtCore.pyqtSlot(str, str, str)
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

    def fit_bounds(self, lon1, lat1, lon2, lat2):
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
            "./js/draw_layer.js",
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
        string = "import('" + module + "').then(module => {module." + function + "("
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
        self.view.page().runJavaScript(string)
