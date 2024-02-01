import os

import geojson

from .layer import Layer
from geopandas import GeoDataFrame
import matplotlib.colors as mcolors

class LineLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)

        pass


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
        self.mapbox.runjs("./js/line_layer.js", "addLayer", arglist=[self.map_id,
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
        self.mapbox.runjs("./js/line_layer.js", "setPaintProperties", arglist=[self.map_id,
                                                                               self.line_color,
                                                                               self.line_width,
                                                                               self.line_opacity,
                                                                               self.fill_color,
                                                                               self.fill_opacity,
                                                                               self.circle_radius])
  
    def deactivate(self):
        self.mapbox.runjs("./js/line_layer.js", "setPaintProperties", arglist=[self.map_id,
                                                                               self.line_color_inactive,
                                                                               self.line_width_inactive,
                                                                               self.line_opacity_inactive,
                                                                               self.fill_color_inactive,
                                                                               self.fill_opacity_inactive,
                                                                               self.circle_radius_inactive])

    # def set_visibility(self, true_or_false):
    #     if true_or_false:
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".line"])
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".circle"])
    #     else:
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".line"])
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".circle"])

