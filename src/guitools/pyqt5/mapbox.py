import os
import functools
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets, QtWebChannel
import json
import numpy as np
import geojson
from urllib.request import urlopen
import urllib
import time
from PIL import Image
import matplotlib
from matplotlib import cm
import rasterio
import rasterio.features
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio import MemoryFile
from requests_html import HTMLSession

from .colorbar import ColorBar
from .widget_group import WidgetGroup
#from .overlays import ImageOverlay

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

        self.layers = {}
        self.id_counter = 0

        view = self.view = QtWebEngineWidgets.QWebEngineView(parent)
#        view.loadFinished.connect(self._loadFinished)
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

        self.layer_group = {}

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reload)
        self.timer.setSingleShot(True)
        self.timer.start(1000)

    def reload(self):
        self.view.page().setWebChannel(self.channel)
        self.channel.registerObject("MapBox", self)
        self.view.load(QtCore.QUrl(self.url))

    # def check_ready(self):
    #     print("Check for ready ...")
    #     js_string = "import('/main.js').then(module => {module.checkMapBoxReady();});"
    #     self.view.page().runJavaScript(js_string)

    def set(self):
        pass

    # @QtCore.pyqtSlot(str)
    # def mapBoxReady(self, ready):
    #     print(ready)
    #     self.ready = True

    @QtCore.pyqtSlot(str)
    def mapMoved(self, coords):
        print("map moved")
        self.callback_module.map_moved(json.loads(coords))

    @QtCore.pyqtSlot(str, str)
    def polygonDrawn(self, coords, feature_id):
        print("A polygon (" + feature_id + ") with coords " + coords + " was drawn in layer ...")
        self.polygon_create_callback(coords)
#        self.polygon_modify_callback

    @QtCore.pyqtSlot(str)
    def featureSelected(self, id):
        print("The feature with ID " + id + " was selected")
#        self.polygon_create_callback(coords)
#        self.polygon_modify_callback

#        self.callback_module.map_moved(json.loads(coords))

    @QtCore.pyqtSlot(str, str, str)
    def layerAdded(self, layer_name, layer_group_name, id):
        pass
#        print("Layer " + layer_name + " added to group " + layer_group_name + " - ID = " + id)
#        layer = self.find_layer(layer_name, layer_group_name)
#        layer.id = id

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


    def draw_polygon(self, layer_id, create=None, modify=None):

        print("Going to draw a polygon !")
        # First find if this layer already exists

        # self.new_polygon        = Polygon()
        # self.new_polygon.id     = None
        # self.new_polygon.create = create
        # self.new_polygon.modify = modify
        # self.new_polygon.layer  = layer_name
        # layer_group_name = "_base"

        js_string = "import('/draw.js').then(module => {module.drawPolygon(" + layer_id + ")});"
        print(js_string)
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

#     def add_image_overlay(self, layer_name, file_name):
#         # js_string = "import('/main.js').then(module => {module.updateImageLayer('" + file_name + "', [" + str(
#         #     extent[0]) + "," + str(extent[1]) + "," + str(extent[2]) + "," + str(
#         #     extent[3]) + "],'" + srs + "','" + proj4 + "');});"
# #        overlay = ImageOverlay(file_name=image_file, file_type="tif")
#         js_string = "import('/main.js').then(module => {module.updateImageLayer('" + file_name + "')});"
# #        print(js_string)
#  #       self.view.page().runJavaScript(js_string)
#         js_string = "import('/main.js').then(module => {module.checkReady();});"
        self.view.page().runJavaScript(js_string)

    def add_image_layer(self,
                        image_file,
                        layer_name=None,
                        layer_group_name=None,
                        legend_title="",
                        cmin=None,
                        cmax=None,
                        cstep=None,
                        decimals=None,
                        colormap="jet"):

        self.id_counter += 1
        id_string = str(self.id_counter)

        dataset = rasterio.open(image_file)

        src_crs = 'EPSG:4326'
        dst_crs = 'EPSG:3857'

        with rasterio.open(image_file) as src:
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })
            bnds = src.bounds

            mem_file = MemoryFile()
            with mem_file.open(**kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest)

                band1 = dst.read(1)

        new_bounds = transform_bounds(dst_crs, src_crs,
                                      dst.bounds[0],
                                      dst.bounds[1],
                                      dst.bounds[2],
                                      dst.bounds[3])
        isn = np.where(band1 < 0.001)
        band1[isn] = np.nan

        band1 = np.flipud(band1)
        cminimum = np.nanmin(band1)
        cmaximum = np.nanmax(band1)

        norm = matplotlib.colors.Normalize(vmin=cminimum, vmax=cmaximum)
        vnorm = norm(band1)

        cmap = cm.get_cmap(colormap)
        im = Image.fromarray(np.uint8(cmap(vnorm) * 255))

        overlay_file = "overlay.png"
        im.save(os.path.join(self.server_path, overlay_file))

        # Make new layer
        layer = Layer(name=layer_name, type="image")
        layer.id = id_string
        layer_group = self.find_layer_group(layer_group_name)
        layer_group[layer_name] = layer

        # Bounds
        bounds = [[new_bounds[0], new_bounds[2]], [new_bounds[3], new_bounds[1]]]
        bounds_string = "[[" + str(bounds[0][0]) + "," + str(bounds[0][1]) + "],[" + str(bounds[1][0]) + "," + str(bounds[1][1]) + "]]"

        # Legend
        clrbar = ColorBar(colormap=colormap, legend_title=legend_title)
        clrbar.make(cmin, cmax, cstep=cstep, decimals=decimals)
        clrmap_string = clrbar.to_json()

        js_string = "import('/main.js').then(module => {module.addImageLayer('" + overlay_file + "','" + id_string + "'," + bounds_string + "," + clrmap_string + ")});"
        self.view.page().runJavaScript(js_string)

    def add_marker_layer(self,
                         collection,
                         marker_file=None,
                         layer_name=None,
                         layer_group_name=None):

        self.id_counter += 1
        id_string = str(self.id_counter)

        layer = Layer(name=layer_name, type="image")
        layer.id = id_string
        layer_group = self.find_layer_group(layer_group_name)
        layer_group[layer_name] = layer
        geojs = geojson.dumps(collection)
        js_string = "import('/main.js').then(module => {module.addMarkerLayer(" + geojs + ",'" + marker_file + "','" + id_string + "','"+ layer_name + "','" + layer_group_name + "')});"
        self.view.page().runJavaScript(js_string)


    def remove_layer(self, layer_name, layer_group_name):
        layer_group = self.find_layer_group(layer_group_name)
        if layer_group:
            if layer_name in layer_group:
                id = layer_group[layer_name].id
                if id:
                    print("Removing " + layer_name + " - id=" + id)
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
            if parent_layer:
                parent_layer[name] = {}
        else:
            if name not in self.layer_group:
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
