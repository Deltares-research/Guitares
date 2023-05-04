import os
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets, QtWebChannel
import json
from urllib.request import urlopen
import urllib
from geopandas import GeoDataFrame

from .layer import Layer, list_layers, find_layer_by_id

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

        url = "http://localhost:" + str(self.gui.server_port) + "/"
        self.url = url


        # while True:
        #     try:
        #
        #         print("Finding server ...")
        #
        #         url = "http://localhost:" + str(server_port) + "/"
        #         self.url = url
        #
        #         urllib.request.urlcleanup()
        #         request = urllib.request.urlopen(url)
        #         response = request.read().decode('utf-8')
        #
        #         print("Found server running at port 3000 ...")
        #
        #         break
        #
        #     except:
        #         print("Waiting for server ...")

        self.ready = False

        self.server_path = self.gui.server_path


        self.setGeometry(0, 0, -1, -1) # this is necessary because otherwise an invisible widget sits over the top left hand side of the screen and block the menu

        view = self.view = QtWebEngineWidgets.QWebEngineView(element.parent.widget)
        channel = self.channel = QtWebChannel.QWebChannel()
        view.page().profile().clearHttpCache()

        self.set_geometry()

        page = WebEnginePage(view, self.gui.js_messages)
        view.setPage(page)
        view.page().setWebChannel(channel)

        channel.registerObject("MapBox", self)

        view.load(QtCore.QUrl(url))

        # file_path = os.path.join(self.server_path, "index.html")
        # local_url = QtCore.QUrl.fromLocalFile(file_path)
        # view.load(local_url)

        self.callback_module = element.module

        self.layer = {}
        self.map_extent = None
        self.map_moved = None
        self.point_clicked_callback = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reload)
        self.timer.setSingleShot(True)
        self.timer.start(1000)


    def reload(self):
        print("Reloading ...")
        self.view.page().setWebChannel(self.channel)
        self.channel.registerObject("MapBox", self)
        self.view.load(QtCore.QUrl(self.url))

    def set(self):
        pass

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.view.setGeometry(x0, y0, wdt, hgt)

    def take_screenshot(self, output_file):
        self.view.grab().save(output_file, b'PNG')

    @QtCore.pyqtSlot(str)
    def mapReady(self, coords):
        coords = json.loads(coords)
        self.ready = True
        self.map_extent = coords
        if hasattr(self.callback_module, "map_ready"):
            self.callback_module.map_ready()
        if hasattr(self.gui.module, "on_map_ready"):
            self.gui.module.on_map_ready()

    @QtCore.pyqtSlot(str)
    def layerStyleSet(self, coords):
        print("Layer style changed.")
        self.redraw_layers()

    @QtCore.pyqtSlot(str)
    def mouseMoved(self, coords):
        coords = json.loads(coords)
        self.map_extent = coords
        # Loop through layers to update each
        layers = list_layers(self.layer)
        for layer in layers:
            layer.update()
        if hasattr(self.callback_module, "map_moved"):
            self.callback_module.map_moved(coords)

    @QtCore.pyqtSlot(str)
    def mapMoved(self, coords):
        coords = json.loads(coords)
        self.map_extent = coords
        # Loop through layers to update each
        layers = list_layers(self.layer)
        for layer in layers:
            layer.update()
        if hasattr(self.callback_module, "map_moved"):
            self.callback_module.map_moved(coords)

    @QtCore.pyqtSlot(str)
    def pointClicked(self, coords):
        coords = json.loads(coords)
        if self.point_clicked_callback:
            self.point_clicked_callback(coords)

    @QtCore.pyqtSlot(str)
    def getMapExtent(self, coords):
        coords = json.loads(coords)
        self.map_extent = coords

    @QtCore.pyqtSlot(str, str)
    def featureClicked(self, layer_id, feature_props):
        # Find layer by ID
        layer = find_layer_by_id(layer_id, self.layer)
        if hasattr(layer, "select"):
            if layer.select:
                layer.select(json.loads(feature_props))

#    @QtCore.pyqtSlot(str, str, str)
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

    def get_extent(self):
        js_string = "import('/js/main.js').then(module => {module.getExtent()});"
        self.view.page().runJavaScript(js_string)

    def click_point(self, callback):
        self.point_clicked_callback = callback
        self.runjs("/js/main.js", "clickPoint")

    def set_center(self, lon, lat):
        self.runjs("/js/main.js", "setCenter", arglist=[lon, lat])

    def set_zoom(self, zoom):
        self.runjs("/js/main.js", "setZoom",  arglist=[zoom])

    def fit_bounds(self, lon1, lat1, lon2, lat2):
        self.runjs("/js/main.js", "fitBounds",  arglist=[lon1, lat1, lon2, lat2])

    def jump_to(self, lon, lat, zoom):
        self.runjs("/js/main.js", "jumpTo",  arglist=[lon, lat, zoom])

    def fly_to(self, lon, lat, zoom):
        self.runjs("/js/main.js", "flyTo",  arglist=[lon, lat, zoom])

    def set_projection(self, projection):
        self.runjs("/js/main.js", "setProjection",  arglist=[projection])

    def set_layer_style(self, style):
        self.runjs("/js/main.js", "setLayerStyle",  arglist=[style])

    def set_terrain(self, true_or_false, exaggeration):
        self.runjs("/js/main.js", "setTerrain",  arglist=[true_or_false, exaggeration])

    def set_mouse_default(self):
        self.runjs("/js/draw.js", "setMouseDefault",  arglist=[])

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
        layers = self.list_layers()
        for layer in layers:
            layer.redraw()

    def compare(self):
        self.runjs("/js/main.js", "compare",  arglist=[])

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
                string = string + json.dumps(arg)
            elif isinstance(arg, list):
                string = string + "[]"
            elif isinstance(arg, GeoDataFrame):
                if len(arg) == 0:
                    string = string + "{}"
                else:    
                    string = string + arg.to_json()
            else:
                string = string + "'" + arg + "'"
            if iarg<len(arglist) - 1:
                string = string + ","
        string = string + ")});"
        # print("JS String")
        # print(string)
        self.view.page().runJavaScript(string)
