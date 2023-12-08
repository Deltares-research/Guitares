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


class MapBoxCompare(QtWidgets.QWidget):
    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.gui = element.gui
        self.element = element

        file_name = os.path.join(self.gui.server_path, "js", "mapbox_compare_defaults.js")
        with open(file_name, "w") as f:
            f.write("var default_compare_style = '" + element.map_style + "';\n")
            f.write("var default_compare_center = [" + str(element.map_center[0]) + "," + str(element.map_center[1]) + "]\n")
            f.write("var default_compare_zoom = " + str(element.map_zoom) + ";\n")
            f.write("var default_compare_projection = '" + element.map_projection + "';\n")

        url = "http://localhost:" + str(self.gui.server_port) + "/mapbox_compare.html"
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

        page = WebEnginePage(view, self.gui.js_messages)
        view.setPage(page)
        view.page().setWebChannel(channel)

        channel.registerObject("MapBoxCompare", self)

        view.load(QtCore.QUrl(url))

        self.callback_module = element.module

        self.layer = {}
        self.map_extent = None
        self.map_moved = None
        self.point_clicked_callback = None
        self.zoom = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reload)
        self.timer.setSingleShot(True)
        self.timer.start(1000)

    def reload(self):
        print("Reloading ...")
        self.view.page().setWebChannel(self.channel)
        self.channel.registerObject("MapBoxCompare", self)
        self.view.load(QtCore.QUrl(self.url))

    def set(self):
        pass

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.view.setGeometry(x0, y0, wdt, hgt)

    def take_screenshot(self, output_file):
        self.view.grab().save(output_file, b"PNG")

    @QtCore.pyqtSlot(str)
    def mapReady(self, inpstr):
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
    def layerStyleSet(self, coords):
        self.redraw_layers()

    # @QtCore.pyqtSlot(str)
    # def mouseMoved(self, coords):
    #     coords = json.loads(coords)
    #     self.map_extent = coords
    #     # Loop through layers to update each
    #     layers = list_layers(self.layer)
    #     for layer in layers:
    #         layer.update()
    #     if hasattr(self.callback_module, "map_moved"):
    #         self.callback_module.map_moved(coords)

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
            self.callback_module.map_moved(coords)

    # @QtCore.pyqtSlot(str)
    # def pointClicked(self, coords):
    #     coords = json.loads(coords)
    #     if self.point_clicked_callback:
    #         self.point_clicked_callback(coords)

    # @QtCore.pyqtSlot(str)
    # def getMapExtent(self, coords):
    #     coords = json.loads(coords)
    #     self.map_extent = coords

    # @QtCore.pyqtSlot(str, str)
    # def featureClicked(self, layer_id, feature_props):
    #     # Find layer by ID
    #     layer = find_layer_by_id(layer_id, self.layer)
    #     if hasattr(layer, "select"):
    #         if layer.select:
    #             layer.select(json.loads(feature_props))

    # @QtCore.pyqtSlot(str, str, str)
    # def featureDrawn(self, feature_collection, feature_id, layer_id):
    #     layer = find_layer_by_id(layer_id, self.layer)
    #     layer.feature_drawn(json.loads(feature_collection), feature_id)

    # @QtCore.pyqtSlot(str, str, str)
    # def featureModified(self, feature_collection, feature_id, layer_id):
    #     layer = find_layer_by_id(layer_id, self.layer)
    #     layer.feature_modified(json.loads(feature_collection), feature_id)

    # @QtCore.pyqtSlot(str, str, str)
    # def featureSelected(self, feature_collection, feature_id, layer_id):
    #     layer = find_layer_by_id(layer_id, self.layer)
    #     layer.feature_selected(json.loads(feature_collection), feature_id)

    # @QtCore.pyqtSlot(str)
    # def featureDeselected(self, layer_id):
    #     layer = find_layer_by_id(layer_id, self.layer)
    #     if layer:
    #         layer.feature_deselected()

    # @QtCore.pyqtSlot(str, str, str)
    # def featureAdded(self, feature_collection, feature_id, layer_id):
    #     layer = find_layer_by_id(layer_id, self.layer)
    #     layer.feature_added(json.loads(feature_collection), feature_id)

    # def get_extent(self):
    #     js_string = "import('/js/main.js').then(module => {module.getExtent()});"
    #     self.view.page().runJavaScript(js_string)

    # def click_point(self, callback):
    #     self.point_clicked_callback = callback
    #     self.runjs("/js/main.js", "clickPoint")

    # def set_center(self, lon, lat):
    #     self.runjs("/js/main.js", "setCenter", arglist=[lon, lat])

    # def set_zoom(self, zoom):
    #     self.runjs("/js/main.js", "setZoom", arglist=[zoom])

    # def fit_bounds(self, lon1, lat1, lon2, lat2):
    #     self.runjs("/js/main.js", "fitBounds", arglist=[lon1, lat1, lon2, lat2])

    def jump_to(self, lon, lat, zoom):
        self.runjs("/js/compare.js", "jumpTo", arglist=[lon, lat, zoom])

    def fly_to(self, lon, lat, zoom):
        self.runjs("/js/compare.js", "flyTo", arglist=[lon, lat, zoom])

    # def set_projection(self, projection):
    #     self.runjs("/js/main.js", "setProjection", arglist=[projection])

    def set_layer_style(self, style):
        self.runjs("/js/compare.js", "setLayerStyle", arglist=[style])

    def set_slider(self, npix):
        self.runjs("/js/compare.js", "setSlider", arglist=[npix])

    # def set_terrain(self, true_or_false, exaggeration):
    #     self.runjs("/js/main.js", "setTerrain", arglist=[true_or_false, exaggeration])

    # def set_mouse_default(self):
    #     self.runjs("/js/draw.js", "setMouseDefault", arglist=[])

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
                    string = string + arg.to_json()
            else:
                string = string + "'" + arg + "'"
            if iarg < len(arglist) - 1:
                string = string + ","
        string = string + ")});"
        self.view.page().runJavaScript(string)
