import os

import geojson

from .layer import Layer
from geopandas import GeoDataFrame
import matplotlib.colors as mcolors

class LineLayer(Layer):
    def __init__(self, map, id, map_id, **kwargs):
        super().__init__(map, id, map_id, **kwargs)

        # Set some default paint values for line layer
        self.circle_radius = 0


    def set_data(self,
                 data):

        self.data = data   

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                return
        else:
            print("Data is not a GeoDataFrame")
            return    

        # Add new layer        
        self.map.runjs("/js/line_layer.js", "addLayer", arglist=[self.map_id,
                                                                     data.to_crs(4326),
                                                                     self.line_color,
                                                                     self.line_width,
                                                                     self.line_opacity,
                                                                     self.fill_color,
                                                                     self.fill_opacity,
                                                                     self.circle_radius])
    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)
        if not self.get_visibility():
            self.set_visibility(False)

    def activate(self):
        self.map.runjs("/js/line_layer.js", "setPaintProperties", arglist=[self.map_id,
                                                                               self.line_color,
                                                                               self.line_width,
                                                                               self.line_opacity,
                                                                               self.fill_color,
                                                                               self.fill_opacity,
                                                                               self.circle_radius])
  
    def deactivate(self):
        self.map.runjs("/js/line_layer.js", "setPaintProperties", arglist=[self.map_id,
                                                                               self.line_color_inactive,
                                                                               self.line_width_inactive,
                                                                               self.line_opacity_inactive,
                                                                               self.fill_color_inactive,
                                                                               self.fill_opacity_inactive,
                                                                               self.circle_radius_inactive])

    # def set_visibility(self, true_or_false):
    #     if true_or_false:
    #         self.map.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".line"])
    #         self.map.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".circle"])
    #     else:
    #         self.map.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".line"])
    #         self.map.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".circle"])

