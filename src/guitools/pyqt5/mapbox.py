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
import logging

from src.guitools.pyqt5.layer import Layer
from src.guitools.pyqt5.colorbar import ColorBar


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
    def layerAdded(self, layer_name, layer_group_name, id):
        pass

    def add_image_layer(self,
                        image_file,
                        layer_name=None,
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

        # Add layer
        self.add_layer(layer_name, id_string)

        # Bounds
        bounds = [[new_bounds[0], new_bounds[2]], [new_bounds[3], new_bounds[1]]]
        bounds_string = "[[" + str(bounds[0][0]) + "," + str(bounds[0][1]) + "],[" + str(bounds[1][0]) + "," + str(bounds[1][1]) + "]]"

        # Legend
        clrbar = ColorBar(colormap=colormap, legend_title=legend_title, scale=scale)
        clrbar.make(cmin, cmax, cstep=cstep, decimals=decimals)
        clrmap_string = clrbar.to_json()

        js_string = "import('/main.js').then(module => {module.addImageLayer('" + overlay_file + "','" + id_string + "'," + bounds_string + "," + clrmap_string + ")});"
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
                         color_by: str = ""):

        self.id_counter += 1
        id_string = str(self.id_counter)

        # Add layer
        self.add_layer(layer_name, id_string)

        feature_collection_string = self.load_geojson_from(geojson_input)

        if color_by:
            js_string = "import('/main.js').then(module => {module.addLineGeojsonLayerColorByProperty(" + feature_collection_string + ",'" + id_string + "','" + layer_name + "','" + layer_name + "','" + color_by + "')});"
        else:
            js_string = "import('/main.js').then(module => {module.addLineGeojsonLayer(" + feature_collection_string + ",'" + id_string + "','" + layer_name + "','" + layer_name + "','" + color + "')});"

        self.view.page().runJavaScript(js_string)

    @QtCore.pyqtSlot(str)
    def coordsClicked(self, coords):
        # print("Coords clicked")
        self.callback_module.coords_clicked(json.loads(coords))

    def remove_layer(self, layer_name):
        if layer_name in self.layers:
            logging.info("Removing " + layer_name)
            self.layers[layer_name].delete()
            del self.layers[layer_name]

    def add_layer(self, layer_id, id_nr):
        # Adds a container layer
        if layer_id not in self.layers:
            self.layers[layer_id] = Layer(self, layer_id, layer_id)
            self.layers[layer_id].map_id = id_nr
        else:
            logging.info("Layer " + layer_id + " already exists.")
        return self.layers[layer_id]

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
            elif isinstance(arg, gpd.GeoDataFrame):
                string = string + arg.to_json()
            else:
                string = string + "'" + arg + "'"
            if iarg<len(arglist) - 1:
                string = string + ","
        string = string + ")});"
        self.view.page().runJavaScript(string)


def tree_traverse(tree, key):
    if key in tree:
        return tree[key]
    for v in filter(dict.__instancecheck__, tree.values()):
        if (found := tree_traverse(v, key)) is not None:
            return found
