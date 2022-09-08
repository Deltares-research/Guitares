import os
import functools
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets, QtWebChannel
import json
import threading
import http.server
import socketserver
from urllib.request import urlopen
from urllib.error import *

from .widget_group import WidgetGroup
#from .overlays import ImageOverlay

class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)


def create_server():

    # Path where web server is running
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    dir_path = os.path.join(dir_path, "mapbox")

    os.chdir(dir_path)
    PORT = 3000
    Handler = http.server.SimpleHTTPRequestHandler
    Handler.extensions_map['.js']     = 'text/javascript'
    Handler.extensions_map['.mjs']    = 'text/javascript'
    Handler.extensions_map['.css']    = 'text/css'
    Handler.extensions_map['.html']   = 'text/html'
    Handler.extensions_map['main.js'] = 'module'
    print("Server path : " + dir_path)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Serving at port", PORT)
        httpd.serve_forever()

class MapBox(QtWidgets.QWidget):
#class MapBox(WidgetGroup):

    def __init__(self, element, parent):
#        super().__init__(element, parent)
        super().__init__(parent)

        # Path where web server is running
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        dir_path = os.path.join(dir_path, "mapbox")

        # Check if something's already running on port 3000.
        try:
            html = urlopen("http://localhost:3000/")
            print("Found server running at port 3000 ...")
        except:
            print("Starting http server ...")
            threading.Thread(target=create_server).start()

#        b = QtWidgets.QWidget(parent)
#        self.widgets.append(b)
        self.map_moved = None

        self.server_path = dir_path

        self.layers = {}

        # b.view = QtWebEngineWidgets.QWebEngineView(parent)
        # channel = QtWebChannel.QWebChannel()
        # b.view.page().profile().clearHttpCache()


        view = self.view = QtWebEngineWidgets.QWebEngineView(parent)
        channel = self.channel = QtWebChannel.QWebChannel()
        view.page().profile().clearHttpCache()
        view.setGeometry(10, 10, 100, 100)


#        b.view.setGeometry(10, 10, 100, 100)

        # x0, y0, wdt, hgt = element["window"].get_position_from_string(self.element["position"], self.parent)
        # b.view.setGeometry(x0, y0, wdt, hgt)

        # page = WebEnginePage(b.view)
        # b.view.setPage(page)


        page = WebEnginePage(view)
        view.setPage(page)


        channel.registerObject("OlMap", self)
        view.page().setWebChannel(channel)

        view.load(QtCore.QUrl('http://localhost:3000/'))

        channel.registerObject("MapBox", self)

#        b.view.page().setWebChannel(channel)

#        b.view.load(QtCore.QUrl('http://localhost:3000/'))

#        b.view.load(QtCore.QUrl('https://opendap.deltares.nl/static/deltares/cosmos/nopp_event_viewer/index.html'))

#        element["widget"] = b


        element["widget"] = view

        self.callback_module = element["module"]

        self.layer_group = {}

    def set(self):
        pass

    @QtCore.pyqtSlot(str)
    def mapMoved(self, coords):
        print(coords)
#        self.callback_module.map_moved(json.loads(coords))
#        self.map_moved(json.loads(coords))

    @QtCore.pyqtSlot(str, str, str)
    def layerAdded(self, layer_name, layer_group_name, id):
        print("Layer " + layer_name + " added to group " + layer_group_name + " - ID = " + id)
        layer = self.find_layer(layer_name, layer_group_name)
        layer.id = id

    @QtCore.pyqtSlot(int, str)
    def polygonAdded(self, id, coords):
#        print("Polygon (id=" + str(id) + ") was added")
#        print(coords)
        # Call the create callback
        if self.polygon_create_callback:
            self.polygon_create_callback(id, coords)

    @QtCore.pyqtSlot(int, str)
    def polygonModified(self, id, coords):
#        print("Polygon (id=" + str(id) + ") was changed")
#        print(coords)
        if self.polygon_modify_callback:
            self.polygon_modify_callback(id, coords)

    @QtCore.pyqtSlot(int, str)
    def polylineAdded(self, id, coords):
#        print("Polyline (id=" + str(id) + ") was added")
#        print(coords)
        if self.polyline_create_callback:
            self.polyline_create_callback(id, coords)

    @QtCore.pyqtSlot(int, str)
    def polylineModified(self, id, coords):
#        print("Polyline (id=" + str(id) + ") was changed")
        if self.polyline_modify_callback:
            self.polyline_modify_callback(id, coords)

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
#        print("Rectangle (id=" + str(id) + ") was changed")
        if self.rectangle_modify_callback:
            self.rectangle_modify_callback(id, coords)

    def add_layer(self, layer_name, layer_parent):
        self.layer[layer_parent][layer_name] = {}
        self.layer[layer_parent][layer_name]["properties"] = LayerProperties()


    def draw_polygon(self, layer_name, create=None, modify=None):
        self.new_polygon        = Polygon()
        self.new_polygon.id     = None
        self.new_polygon.create = create
        self.new_polygon.modify = modify
        self.new_polygon.layer  = layer_name
        layer_group_name = "_base"
        js_string = "import('/main.js').then(module => {module.drawPolygon('" + layer_group_name + "','" + layer_name + "');});"
        self.view.page().runJavaScript(js_string)
        self.polygon_create_callback = None
        self.polygon_modify_callback = None
        if create:
            self.polygon_create_callback = create
        if modify:
            self.polygon_modify_callback = modify

    def draw_polyline(self, layer_name, create=None, modify=None):
        layer_group_name = "_base"
        js_string = "import('/main.js').then(module => {module.drawPolyline('" + layer_group_name + "','" + layer_name + "');});"
        self.view.page().runJavaScript(js_string)
        self.polyline_create_callback = None
        self.polyline_modify_callback = None
        if create:
            self.polyline_create_callback = create
        if modify:
            self.polyline_modify_callback = modify

    def draw_point(self, layer_group_name, layer_name):
        js_string = "import('/main.js').then(module => {module.drawPoint('" + layer_group_name + "','" + layer_name + "');});"
        self.view.page().runJavaScript(js_string)

    def draw_rectangle(self, layer_name, create=None, modify=None):
        layer_group_name = "_base"
        js_string = "import('/main.js').then(module => {module.drawRectangle('" + layer_group_name + "','" + layer_name + "');});"
        self.view.page().runJavaScript(js_string)
        self.rectangle_create_callback = None
        self.rectangle_modify_callback = None
        if create:
            self.rectangle_create_callback = create
        if modify:
            self.rectangle_modify_callback = modify

    def update_image_layer(self, file_name, extent, srs, proj4):
        js_string = "import('/main.js').then(module => {module.updateImageLayer('" + file_name + "', [" + str(
            extent[0]) + "," + str(extent[1]) + "," + str(extent[2]) + "," + str(
            extent[3]) + "],'" + srs + "','" + proj4 + "');});"
        self.view.page().runJavaScript(js_string)

    def add_image_overlay(self, layer_name, file_name):
        # js_string = "import('/main.js').then(module => {module.updateImageLayer('" + file_name + "', [" + str(
        #     extent[0]) + "," + str(extent[1]) + "," + str(extent[2]) + "," + str(
        #     extent[3]) + "],'" + srs + "','" + proj4 + "');});"
#        overlay = ImageOverlay(file_name=image_file, file_type="tif")
        js_string = "import('/main.js').then(module => {module.updateImageLayer('" + file_name + "')});"
        print(js_string)
 #       self.view.page().runJavaScript(js_string)

    def add_image_layer(self, file_name, layer_name, layer_group_name, bounds):
        # js_string = "import('/main.js').then(module => {module.updateImageLayer('" + file_name + "', [" + str(
        #     extent[0]) + "," + str(extent[1]) + "," + str(extent[2]) + "," + str(
        #     extent[3]) + "],'" + srs + "','" + proj4 + "');});"
#        overlay = ImageOverlay(file_name=image_file, file_type="tif")
        # First copy image over

        layer = Layer(name=layer_name, type="image")
        layer_group = self.find_layer_group(layer_group_name)
        layer_group[layer_name] = layer
        bounds_string = "[[" + str(bounds[0][0]) + "," + str(bounds[0][1]) + "],[" + str(bounds[1][0]) + "," + str(bounds[1][1]) + "]]"
        js_string = "import('/main.js').then(module => {module.addImageLayer('" + file_name + "','" + layer_name + "','" + layer_group_name + "'," + bounds_string + ")});"
#        print(js_string)
        self.view.page().runJavaScript(js_string)

    def remove_layer(self, layer_name, layer_group_name):
        layer_group = self.find_layer_group(layer_group_name)
        id = layer_group[layer_name].id
        js_string = "import('/main.js').then(module => {module.removeLayer('" + id + "')});"
        self.view.page().runJavaScript(js_string)
        # Now remove layer from layer group
        layer_group.pop(layer_name)

    # def show_image_layer(self):
    #     js_string = "import('/main.js').then(module => {module.showImageLayer()});"
    #     self.view.page().runJavaScript(js_string)

    def add_layer_group(self, name, parent=None):
        if parent:
            parent_layer = self.find_layer_group(parent)
            parent_layer[name] = {}
        else:
            self.layer_group[name] = {}

    def find_layer_group(self, name):
        layer_group = tree_traverse(self.layer_group, name)
        return layer_group

    def find_layer(self, layer_name, layer_group_name):
        layer_group = tree_traverse(self.layer_group, layer_group_name)
        return layer_group[layer_name]

class Polygon:
    def __init__(self):
        pass
    def plot(self):
        pass
    def delete(self):
        pass
    def add_to(self, layer):
        pass
    def set_color(self, color):
        pass

class Layer:
    def __init__(self, name=None, type=None):
        self.name = name
        self.id   = None
        self.type = type
        self.color = "k"
    def update(self):
        pass
    def remove(self):
        pass
    def add_to_group(self, layer_group_name):
        pass


def tree_traverse(tree, key):
    if key in tree:
        return tree[key]
    for v in filter(dict.__instancecheck__, tree.values()):
        if (found := tree_traverse(v, key)) is not None:
            return found
