import os
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets, QtWebChannel
import json
from urllib.request import urlopen
import urllib
from geopandas import GeoDataFrame

from .layer import Layer, list_layers, find_layer_by_id
from guitares.gui import get_position

class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, view, print_messages):
        super().__init__(view)
        self.print_messages = print_messages
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if self.print_messages:
            print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)

class MapBox(QtWidgets.QWidget):
    def __init__(self, element, parent, gui):
        super().__init__(parent)

        self.gui = gui

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

        view = self.view = QtWebEngineWidgets.QWebEngineView(parent)
        channel = self.channel = QtWebChannel.QWebChannel()
        view.page().profile().clearHttpCache()

        x0, y0, wdt, hgt = get_position(element["position"], parent, self.gui.resize_factor)
        view.setGeometry(x0, y0, wdt, hgt)

        page = WebEnginePage(view, self.gui.js_messages)
        view.setPage(page)
        view.page().setWebChannel(channel)

        channel.registerObject("MapBox", self)

        view.load(QtCore.QUrl(url))

        self.callback_module = element["module"]

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
#    def featureClicked2(self, layer_id, feature_props):
    def featureClicked(self, layer_id, feature_props):
        # Find layer by ID
        layer = find_layer_by_id(layer_id, self.layer)
        if hasattr(layer, "select_callback"):
            layer.select_callback(json.loads(feature_props))

#    @QtCore.pyqtSlot(str, str, str)
    @QtCore.pyqtSlot(str, str)
    def featureDrawn(self, feature_collection, feature_id):
        self.active_draw_layer.feature_drawn(json.loads(feature_collection), feature_id)

    @QtCore.pyqtSlot(str, str)
    def featureModified(self, feature_collection, feature_id):
        self.active_draw_layer.feature_modified(json.loads(feature_collection), feature_id)

    @QtCore.pyqtSlot(str, str)
    def featureSelected(self, feature_collection, feature_id):
        self.active_draw_layer.feature_selected(json.loads(feature_collection), feature_id)

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
                string = string + arg.to_json()
            else:
                string = string + "'" + arg + "'"
            if iarg<len(arglist) - 1:
                string = string + ","
        string = string + ")});"
        self.view.page().runJavaScript(string)
