import os
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets, QtWebChannel
import json
from urllib.request import urlopen
import urllib

from .layer import Layer, list_layers

class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)

class MapBox(QtWidgets.QWidget):

    def __init__(self, element, parent, server_path, server_port):
        super().__init__(parent)

        while True:
            try:

                print("Finding server ...")

                url = "http://localhost:" + str(server_port) + "/"
                self.url = url

                urllib.request.urlcleanup()
                request = urllib.request.urlopen(url)
                response = request.read().decode('utf-8')

                print("Found server running at port 3000 ...")

                break

            except:
                print("Waiting for server ...")

        self.server_path = server_path

        self.map_moved = None

        self.id_counter = 0

        self.setGeometry(0, 0, -1, -1) # this is necessary because otherwise an invisible widget sits over the top left hand side of the screen and block the menu

        view = self.view = QtWebEngineWidgets.QWebEngineView(parent)
        channel = self.channel = QtWebChannel.QWebChannel()
        view.page().profile().clearHttpCache()
        view.setGeometry(10, 10, 100, 100)

        page = WebEnginePage(view)
        view.setPage(page)
        view.page().setWebChannel(channel)

        channel.registerObject("MapBox", self)

        view.load(QtCore.QUrl('http://localhost:' + str(server_port) + '/'))

        element["widget"] = view

        self.callback_module = element["module"]

        self.layer = {}
        self.map_extent = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reload)
        self.timer.setSingleShot(True)
        self.timer.start(1000)

    def reload(self):
#        print("Reloading ...")
        self.view.page().setWebChannel(self.channel)
        self.channel.registerObject("MapBox", self)
        self.view.load(QtCore.QUrl(self.url))

    def set(self):
        pass

    @QtCore.pyqtSlot(str)
    def mapReady(self, coords):
        coords = json.loads(coords)
        self.map_extent = coords
        self.callback_module.map_ready()

    @QtCore.pyqtSlot(str)
    def mapMoved(self, coords):
        coords = json.loads(coords)
        self.map_extent = coords
        # Loop through layers to update each
        layers = list_layers(self.layer)
        for layer in layers:
            layer.update()
        self.callback_module.map_moved(coords)

    @QtCore.pyqtSlot(str)
    def getMapExtent(self, coords):
        coords = json.loads(coords)
        self.map_extent = coords

    @QtCore.pyqtSlot(str, str, str)
    def featureDrawn(self, coord_string, feature_id, feature_type):
        self.active_draw_layer.feature_drawn(json.loads(coord_string), feature_id, feature_type)

    @QtCore.pyqtSlot(str, str, str)
    def featureModified(self, coord_string, feature_id, feature_type):
        self.active_draw_layer.feature_modified(json.loads(coord_string), feature_id, feature_type)

    # @QtCore.pyqtSlot(int, str)
    # def polylineAdded(self, id, coords):
    #     if self.polyline_create_callback:
    #         self.polyline_create_callback(id, coords)

    @QtCore.pyqtSlot(str)
    def featureSelected(self, feature_id):
        self.active_draw_layer.feature_selected(feature_id)

#     @QtCore.pyqtSlot(int, str)
#     def polylineModified(self, id, coords):
# #        print("Polyline (id=" + str(id) + ") was changed")
#         if self.polyline_modify_callback:
#             self.polyline_modify_callback(id, coords)

    @QtCore.pyqtSlot(int, str)
    def pointAdded(self, id, coords):
        print("Point (id=" + str(id) + ") was added")

    @QtCore.pyqtSlot(int, str)
    def pointModified(self, id, coords):
        print("Point (id=" + str(id) + ") was changed")

    @QtCore.pyqtSlot(int, str)
    def rectangleAdded(self, id, coords):
#        print("Rectngle (id=" + str(id) + ") was added")
        if self.rectangle_create_callback:
            self.rectangle_create_callback(id, coords)

    @QtCore.pyqtSlot(int, str)
    def rectangleModified(self, id, coords):
        if self.rectangle_modify_callback:
            self.rectangle_modify_callback(id, coords)

    def get_extent(self):
        js_string = "import('./js/main.js').then(module => {module.getExtent()});"
        self.view.page().runJavaScript(js_string)

    def set_center(self, lon, lat):
        js_string = "import('./js/main.js').then(module => {module.setCenter(" + str(lon) + "," + str(lat) + ");});"
        self.view.page().runJavaScript(js_string)

    def set_zoom(self, zoom):
        js_string = "import('./js/main.js').then(module => {module.setZoom(" + str(zoom) + ");});"
        self.view.page().runJavaScript(js_string)

    def jump_to(self, lon, lat, zoom):
        js_string = "import('./js/main.js').then(module => {module.jumpTo(" + str(lon) + "," + str(lat) + "," + str(zoom) + ");});"
        self.view.page().runJavaScript(js_string)

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

    # def delete_layer(self, layer_id):
    #     if layer_id in self.layer:
    #         self.layer[layer_id].delete()

    # def find_layer_by_id(self, id):
    #     layer_list = self.list_layers()
    #     for layer in layer_list:
    #         if layer.id == id:
    #             return layer
    #     return None
