import os

import geojson

from .layer import Layer
from geopandas import GeoDataFrame
import matplotlib.colors as mcolors

class GeoJSONLayer(Layer):
    def __init__(self, mapbox, id, map_id,
                 data=None,
                 file_name=None,
                 select=None,
                 type=None,
                 selection_type="single",
                 fill_color="red",
                 fill_opacity=0.75,
                 line_width=1):
        super().__init__(mapbox, id, map_id)
        self.active = False
        self.type   = "geojson"
        self.select_callback = select

        fill_color = mcolors.to_hex(fill_color)

        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if file_name:
                with open(os.path.join(self.mapbox.server_path, "overlays", file_name), "w") as f:
                    f.write(data.to_json())
                data = "./overlays/" + file_name
            else:
                data = data.to_json()
        else:
            data = []
        if type == "polygon_selector":
            self.mapbox.runjs("./js/geojson_layer_polygon_selector.js", "addLayer", arglist=[self.map_id,
                                                                                             data,
                                                                                             fill_color,
                                                                                             fill_opacity,
                                                                                             line_width,
                                                                                             selection_type])
        else:
            self.mapbox.runjs("./js/geojson_layer_polygon_selector.js", "addLayer", arglist=[self.map_id, data])

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


    def clear(self):
        self.active = False
        self.mapbox.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])

    def update(self):
        pass

    def set_data(self,
                 data,
                 legend_title="",
                 crs=None):
        self.mapbox.runjs("/js/geojson_layer.js", "setData", arglist=[self.map_id, data])
