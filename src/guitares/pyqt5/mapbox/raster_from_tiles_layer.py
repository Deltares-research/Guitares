import os
from PIL import Image
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
import rasterio
import rasterio.features
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio import MemoryFile
from rasterio.transform import Affine
import geopandas as gpd
import pandas as pd
import shapely
#import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import numpy as np

from .colorbar import ColorBar

from .layer import Layer

from cht_tiling.tiling import make_floodmap_overlay

class RasterFromTilesLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        self.active = False
        self.type   = "raster_from_tiles"
        self.new    = True
        self.file_name = map_id + ".png"

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


    def clear(self):
        self.active = False
        js_string = "import('/js/main.js').then(module => {module.removeLayer('" + self.map_id + "')});"
        self.mapbox.view.page().runJavaScript(js_string)

    def set_data(self,
                 legend_title="",
                 color_values=None,
                 option=None,
                 water_level=None,
                 cmin=None,
                 cmax=None,
                 cstep=None,
                 decimals=None,
                 colormap=None,
                 index_path=None,
                 topobathy_path=None,
                 zbmax=0.0,
                 opacity=0.5):
        
        self.data = {}
        self.data["option"] = option
        self.data["water_level"] = water_level
        self.data["index_path"] = index_path
        self.data["topobathy_path"] = topobathy_path
        self.data["color_values"] = color_values
        self.data["legend_title"] = legend_title
        self.data["cmin"] = cmin
        self.data["cmax"] = cmax
        self.data["cstep"] = cstep
        self.data["decimals"] = decimals
        self.data["colormap"] = colormap
        self.data["zbmax"] = zbmax
        self.data["opacity"] = opacity

        self.update()

    def update(self):

        overlay_file = os.path.join(self.mapbox.server_path, 'overlays', self.file_name)
        overlay_url  = "./overlays/" + self.file_name

        coords = self.mapbox.map_extent
        xl = [coords[0][0], coords[1][0]]
        yl = [coords[0][1], coords[1][1]]
        wdt = self.mapbox.view.geometry().width()
        hgt = self.mapbox.view.geometry().height()

        xb, yb = make_floodmap_overlay(self.data["water_level"],
                                       self.data["index_path"],
                                       self.data["topobathy_path"],
                                       npixels=[wdt, hgt],
                                       lon_range=xl,
                                       lat_range=yl,  
                                       option="deterministic",
                                       color_values=self.data["color_values"],
                                       caxis=None,
                                       zbmax=self.data["zbmax"],
                                       depth=None,
                                       quiet=False,
                                       file_name=overlay_file)

        # Bounds
        bounds_string = "[[" + str(xb[0]) + "," + str(xb[1]) + "],[" + str(yb[0]) + "," + str(yb[1]) + "]]"

        # Legend
        # clrbar = ColorBar(colormap=colormap, legend_title=legend_title)
        # clrbar.make(cmin, cmax, cstep=cstep, decimals=decimals)
        # clrmap_string = clrbar.to_json()
        clrbar = ColorBar(color_values=self.data["color_values"], legend_title=self.data["legend_title"])
        clrbar.make(0.0, 0.0, decimals=self.data["decimals"])
        clrmap_string = clrbar.to_json()
#        clrmap_string = ""

        if type(self.mapbox).__name__ == "MapBox": 
            # Regular map box
            if self.new:
                js_string = "import('/js/image_layer.js').then(module => {module.addLayer('" + overlay_url + "','" + self.map_id + "'," + bounds_string + "," + clrmap_string + ")});"
                self.mapbox.view.page().runJavaScript(js_string)
            else:
                js_string = "import('/js/image_layer.js').then(module => {module.updateLayer('" + overlay_url + "','" + self.map_id + "'," + bounds_string + "," + clrmap_string + ")});"
                self.mapbox.view.page().runJavaScript(js_string)
            self.mapbox.runjs("./js/image_layer.js", "setOpacity", arglist=[self.map_id, self.data["opacity"]])
        elif type(self.mapbox == "MapBoxCompare"): 
            # Compare map box
            if self.new:
                js_string = "import('/js/image_layer_compare.js').then(module => {module.addLayer('" + overlay_url + "','" + self.map_id + "'," + bounds_string + "," + clrmap_string + ",'" + self.side + "')});"
                self.mapbox.view.page().runJavaScript(js_string)
#                self.mapbox.runjs("/js/image_layer_compare.js", "addLayer", arglist=[overlay_url, self.map_id, bounds_string, clrmap_string, self.side])
            else:
                js_string = "import('/js/image_layer_compare.js').then(module => {module.updateLayer('" + overlay_url + "','" + self.map_id + "'," + bounds_string + "," + clrmap_string + ",'" + self.side + "')});"
                self.mapbox.view.page().runJavaScript(js_string)
#                self.mapbox.runjs("/js/image_layer_compare.js", "updateLayer", arglist=[overlay_url, self.map_id, bounds_string, clrmap_string, self.side])
            self.mapbox.runjs("./js/image_layer_compare.js", "setOpacity", arglist=[self.map_id, self.data["opacity"], self.side])

        self.new = False


    def redraw(self):
        self.new = True
        self.update()
