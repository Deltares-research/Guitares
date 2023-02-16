import os
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore, QtWidgets, QtWebChannel
import json
import numpy as np
import geojson
from urllib.request import urlopen
import urllib
from PIL import Image
import matplotlib
from matplotlib import cm
import rasterio
import rasterio.features
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio import MemoryFile
from typing import Union
import geopandas as gpd
from shapely.geometry import LineString
from pathlib import Path

from .colorbar import ColorBar


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
        self.clicked_coords = None

        self.layers = {}
        self.id_counter = 0

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

        self.layer_group = {}

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reload)
        self.timer.setSingleShot(True)
        self.timer.start(1000)

    def reload(self):
        self.view.page().setWebChannel(self.channel)
        self.channel.registerObject("MapBox", self)
        self.view.load(QtCore.QUrl(self.url))

    def set(self):
        pass

    @QtCore.pyqtSlot(str)
    def mapMoved(self, coords):
        self.callback_module.map_moved(json.loads(coords))

    @QtCore.pyqtSlot(str, str, str)
    def polygonDrawn(self, coord_string, feature_id, layer_id):
        self.active_layer.create_feature(json.loads(coord_string), feature_id, "polygon")

    @QtCore.pyqtSlot(str, str, str)
    def featureModified(self, coord_string, feature_id, layer_id):
        coords = json.loads(coord_string)
        self.active_layer.modify_feature(coords, feature_id, "polygon")

    @QtCore.pyqtSlot(int, str)
    def polylineAdded(self, id, coords):
        if self.polyline_create_callback:
            self.polyline_create_callback(id, coords)

    @QtCore.pyqtSlot(str)
    def featureSelected(self, feature_id):
        self.active_layer.select_feature(feature_id)

    @QtCore.pyqtSlot(str, str, str)
    def layerAdded(self, layer_name, layer_group_name, id):
        pass

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
        if self.rectangle_modify_callback:
            self.rectangle_modify_callback(id, coords)

    def add_layer(self, layer_id, type, create=None, modify=None, select=None):

        # First add layer group
        ids = layer_id.split(".")
        lid = ids[-1]
        ids = ids[:-1]
        idstr = ids[0]
        for j, id in enumerate(ids):
            if j>0:
                idstr = idstr + "." + id
        self.add_layer_group(idstr)

        # Now add the layer
        if type == "draw":
            layer = DrawLayer(self, layer_id, create=create, modify=modify, select=select)

        nids = len(ids)

        if nids == 1:
            self.layer[ids[0]][lid] = layer
        elif nids == 2:
            self.layer[ids[0]][ids[1]][lid] = layer
        elif nids == 3:
            self.layer[ids[0]][ids[1]][ids[2]][lid] = layer
        elif nids == 4:
            self.layer[ids[0]][ids[1]][ids[2]][ids[3]][lid] = layer
        elif nids == 5:
            self.layer[ids[0]][ids[1]][ids[2]][ids[3]][ids[4]][lid] = layer

        return layer

    def delete_layer(self, layer_id):

        layer = self.find_layer_by_id(layer_id)

        if layer:

            layer.clear()

            # First add layer group
            ids = layer_id.split(".")
            lid = ids[-1]
            ids = ids[:-1]
            nids = len(ids)

            if nids == 1:
                self.layer[ids[0]].pop(lid)
            elif nids == 2:
                self.layer[ids[0]][ids[1]].pop(lid)
            elif nids == 3:
                self.layer[ids[0]][ids[1]][ids[2]].pop(lid)
            elif nids == 4:
                self.layer[ids[0]][ids[1]][ids[2]][ids[3]].pop(lid)
            elif nids == 5:
                self.layer[ids[0]][ids[1]][ids[2]][ids[3]][ids[4]].pop(lid)


    def activate_layer(self, layer_id):
        layer = self.find_layer_by_id(layer_id)
        if layer:
            layer.activate()
        else:
            print("Error! No layer found with id " + layer_id)

    def deactivate_layer(self, layer_id):
        layer = self.find_layer_by_id(layer_id)
        if layer:
            layer.deactivate()
        else:
            print("Error! No layer found with id " + layer_id)


    def add_layer_group(self, layer_group_id):
        ids = layer_group_id.split(".")
        id = ids[0]
        if ids[0] not in self.layer:
            self.layer[ids[0]] = {"_id": id}
        if len(ids)>1:
            id = id + "." + ids[1]
            if ids[1] not in self.layer[ids[0]]:
                self.layer[ids[0]][ids[1]] = {"_id": id}
        if len(ids)>2:
            id = id + "." + ids[2]
            if ids[2] not in self.layer[ids[0]][ids[1]]:
                self.layer[ids[0]][ids[1]][ids2[2]] = {"_id": id}
        if len(ids)>3:
            id = id + "." + ids[3]
            if ids[3] not in self.layer[ids[0]][ids[1]][ids[2]]:
                self.layer[ids[0]][ids[1]][ids2[2]][ids[3]] = {"_id": id}
        if len(ids)>4:
            id = id + "." + ids[4]
            if ids[3] not in self.layer[ids[0]][ids[1]][ids[2]][ids[3]]:
                self.layer[ids[0]][ids[1]][ids2[2]][ids[3]][ids[4]] = {"_id": id}

    def find_layer_by_id(self, id):
        layer_list = self.list_layers()
        for layer in layer_list:
            if layer.id == id:
                return layer
        return None

    def draw_polygon(self, layer_id):
        layer = self.find_layer_by_id(layer_id)
        if layer:
            layer.draw_polygon()
        else:
            print("Error! No layer found with id " + layer_id)

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
                        colormap="jet",
                        scale="linear"):
        self.id_counter += 1
        id_string = str(self.id_counter)

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
            no_data_value = src.nodata

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
        band1 = band1.astype(np.float32)
        isnull = np.where(band1 == no_data_value)
        band1[isnull] = np.nan

        band1 = np.flipud(band1)
        cminimum = np.nanmin(band1)
        cmaximum = np.nanmax(band1)

        if scale == "linear":
            norm = matplotlib.colors.Normalize(vmin=cminimum, vmax=cmaximum)
            vnorm = norm(band1)
        elif scale == "discrete":
            vnorm = band1

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
        clrbar = ColorBar(colormap=colormap, legend_title=legend_title, scale=scale)
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

    @staticmethod
    def load_geojson_from(geojson_input: Union[str, Path, LineString]):
        if isinstance(geojson_input, (Path, str)):
            if Path(geojson_input).is_file():
                with open(geojson_input) as data_file:
                    feature_collection = geojson.load(data_file)
                    feature_collection = str(feature_collection)
            else:
                feature_collection = geojson_input
        elif isinstance(geojson_input, LineString):
            feature_collection = gpd.GeoSeries([geojson_input]).to_json()
        return feature_collection

    def add_line_geojson(self,
                         geojson_input: Union[str, Path],
                         color: str = None,
                         layer_name: str = None,
                         layer_group_name: str = None,
                         color_by: str = ""):

        self.id_counter += 1
        id_string = str(self.id_counter)

        layer = Layer(name=layer_name, type="lines")
        layer.id = id_string
        layer_group = self.find_layer_group(layer_group_name)
        if not layer_group:
            self.add_layer_group(layer_group_name)
            layer_group = self.find_layer_group(layer_group_name)
        layer_group[layer_name] = layer

        feature_collection_string = self.load_geojson_from(geojson_input)

        if color_by:
            js_string = "import('/main.js').then(module => {module.addLineGeojsonLayerColorByProperty(" + feature_collection_string + ",'" + id_string + "','" + layer_name + "','" + layer_group_name + "','" + color_by + "')});"
        else:
            js_string = "import('/main.js').then(module => {module.addLineGeojsonLayer(" + feature_collection_string + ",'" + id_string + "','" + layer_name + "','" + layer_group_name + "','" + color + "')});"

        self.view.page().runJavaScript(js_string)

    @QtCore.pyqtSlot(str)
    def coordsClicked(self, coords):
        # print("Coords clicked")
        self.callback_module.coords_clicked(json.loads(coords))

    def remove_raster_layer(self, layer_name, layer_group_name):
        layer_group = self.find_layer_group(layer_group_name)
        if layer_group:
            if layer_group_name == layer_group.name:
                id = layer_group.id
                if id:
                    print("Removing " + layer_name + " - id=" + id)
                    js_string = "import('/main.js').then(module => {module.removeLayer('" + id + "')});"
                    self.view.page().runJavaScript(js_string)

    def remove_geojson_layer(self, layer_name, layer_group_name):
        layer_group = self.find_layer_group(layer_group_name)
        if layer_group:
            try:
                existing_layer_name = layer_group[layer_name].name
            except TypeError:
                existing_layer_name = layer_group.name

            if layer_name == existing_layer_name:
                layer_id = layer_group[layer_name].id
                if layer_id:
                    print("Removing " + layer_name + " - id=" + layer_id)
                    js_string = "import('/main.js').then(module => {module.removeLayer('" + layer_id + "')});"
                    self.view.page().runJavaScript(js_string)

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
