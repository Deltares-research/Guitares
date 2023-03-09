import os

import geojson

from .layer import Layer
from geopandas import GeoDataFrame
import matplotlib.colors as mcolors

class GeoJSONLayerCircle(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)

        pass


    def set_data(self,
                 data,
                 legend_title="",
                 crs=None):

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                data = GeoDataFrame()

        # Remove existing layer        
        self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id])

        # Add new layer        
        self.mapbox.runjs("./js/geojson_layer_circle.js", "addLayer", arglist=[self.map_id,
                                                                                        data,
                                                                                        self.line_color,
                                                                                        self.line_width,
                                                                                        self.line_style,
                                                                                        self.line_opacity,
                                                                                        self.fill_color,
                                                                                        self.fill_opacity,
                                                                                        self.circle_radius])

    def activate(self):
        self.mapbox.runjs("./js/geojson_layer_circle.js", "setPaintProperties", arglist=[self.map_id,
                                                                                         self.line_color,
                                                                                         self.line_width,
                                                                                         self.line_style,
                                                                                         self.line_opacity,
                                                                                         self.fill_color,
                                                                                         self.fill_opacity,
                                                                                         self.circle_radius])
  
    def deactivate(self):
        self.mapbox.runjs("./js/geojson_layer_circle.js", "setPaintProperties", arglist=[self.map_id,
                                                                                         self.line_color_inactive,
                                                                                         self.line_width_inactive,
                                                                                         self.line_style_inactive,
                                                                                         self.line_opacity_inactive,
                                                                                         self.fill_color_inactive,
                                                                                         self.fill_opacity_inactive,
                                                                                         self.circle_radius_inactive])

    # def activate(self):
    #     self.active = True

    # def deactivate(self):
    #     self.active = False

    # def clear(self):
    #     self.active = False
    #     self.mapbox.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])

    # def update(self):
    #     pass

    # def set_data(self,
    #              data,
    #              legend_title="",
    #              crs=None):
    #     # Make sure this is not an empty GeoDataFrame
    #     if isinstance(data, GeoDataFrame):
    #         # Data is GeoDataFrame
    #         if len(data) > 0:
    #             # Convert GDF to geojson
    #             data = data.to_json()
    #             self.mapbox.runjs("/js/geojson_layer.js", "setData", arglist=[self.map_id, data])

    def set_visibility(self, true_or_false):
        if true_or_false:
            self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".fill"])
            self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".line"])
        else:
            self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".fill"])
            self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".line"])
