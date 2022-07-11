import os
import functools
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets, QtWebChannel
import json
import threading
import http.server
import socketserver


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)


def create_server():
    os.chdir("d:\\projects\\python\\openlayers_v04")
    PORT = 3000
    Handler = http.server.SimpleHTTPRequestHandler
    Handler.extensions_map['.js']     = 'text/javascript'
    Handler.extensions_map['.mjs']    = 'text/javascript'
    Handler.extensions_map['.css']    = 'text/css'
    Handler.extensions_map['.html']   = 'text/html'
    Handler.extensions_map['main.js'] = 'module'
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

class OlMap(QtWidgets.QWidget):

    def __init__(self, element, parent):
        super().__init__(parent)

#        threading.Thread(target=create_server).start()

        self.map_moved = None

        view = self.view = QtWebEngineWidgets.QWebEngineView(parent)
        channel = self.channel = QtWebChannel.QWebChannel()
        view.setGeometry(10, 10, 100, 100)

        page = WebEnginePage(view)
        view.setPage(page)

        channel.registerObject("OlMap", self)
        view.page().setWebChannel(channel)

        view.load(QtCore.QUrl('http://localhost:3000/'))

#        view.load(QtCore.QUrl('https://opendap.deltares.nl/static/deltares/cosmos/nopp_event_viewer/index.html'))

        element["widget"] = view

        self.callback_module = element["module"]

        self.layer = {}

    @QtCore.pyqtSlot(str)
    def mapMoved(self, coords):
#        print(coords)
        self.callback_module.map_moved(json.loads(coords))
#        self.map_moved(json.loads(coords))

    @QtCore.pyqtSlot(int, str)
    def polygonAdded(self, id, coords):
#        print("Polygon (id=" + str(id) + ") was added")
#        print(coords)
        # Call the create callback
        if self.polygon_create_callback:
            self.polygon_create_callback(id, coords)

    @QtCore.pyqtSlot(int, str)
    def polygonModified(self, id, coords):
        print("Polygon (id=" + str(id) + ") was changed")
        print(coords)

    @QtCore.pyqtSlot(int, str)
    def polylineAdded(self, id, coords):
        print("Polyline (id=" + str(id) + ") was added")
        print(coords)

    @QtCore.pyqtSlot(int, str)
    def polylineModified(self, id, coords):
        print("Polyline (id=" + str(id) + ") was changed")

    @QtCore.pyqtSlot(int, str)
    def pointAdded(self, id, coords):
        print("Point (id=" + str(id) + ") was added")

    @QtCore.pyqtSlot(int, str)
    def pointModified(self, id, coords):
        print("Point (id=" + str(id) + ") was changed")

    @QtCore.pyqtSlot(int, str)
    def rectangleAdded(self, id, coords):
        print("Rectngle (id=" + str(id) + ") was added")

    @QtCore.pyqtSlot(int, str)
    def rectangleModified(self, id, coords):
        print("Rectangle (id=" + str(id) + ") was changed")

    def add_layer(self, layer_name, layer_parent):
        self.layer[layer_parent][layer_name] = {}
        self.layer[layer_parent][layer_name]["properties"] = LayerProperties()


    def draw_polygon(self, layer_name, create=None, modify=None):
        self.new_polygon        = Polygon()
        self.new_polygon.id     = None
        self.new_polygon.create = create
        self.new_polygon.modify = modify
        self.new_polygon.layer  = layer_name
        js_string = "import('/main.js').then(module => {module.drawPolygon('" + layer_group_name + "','" + layer_name + "');});"
        self.view.page().runJavaScript(js_string)
        # self.polygon_create_callback = None
        # self.polygon_modify_callback = None
        # if create:
        #     self.polygon_create_callback = create
        # if modify:
        #     self.polygon_modify_callback = modify

    def draw_polyline(self, layer_group_name, layer_name):
        js_string = "import('/main.js').then(module => {module.drawPolyline('" + layer_group_name + "','" + layer_name + "');});"
        self.view.page().runJavaScript(js_string)

    def draw_point(self, layer_group_name, layer_name):
        js_string = "import('/main.js').then(module => {module.drawPoint('" + layer_group_name + "','" + layer_name + "');});"
        self.view.page().runJavaScript(js_string)

    def draw_rectangle(self, layer_group_name, layer_name):
        js_string = "import('/main.js').then(module => {module.drawRectangle('" + layer_group_name + "','" + layer_name + "');});"
        self.view.page().runJavaScript(js_string)

    def update_image_layer(self, file_name, extent, srs, proj4):
        js_string = "import('/main.js').then(module => {module.updateImageLayer('" + file_name + "', [" + str(
            extent[0]) + "," + str(extent[1]) + "," + str(extent[2]) + "," + str(
            extent[3]) + "],'" + srs + "','" + proj4 + "');});"
        self.view.page().runJavaScript(js_string)

class LayerProperties:
    def __init__(self, name):
        self.color = "k"

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
