import os

import geojson

from .layer import Layer
from geopandas import GeoDataFrame
import matplotlib.colors as mcolors

class LineSelectorLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)

        pass


    def set_data(self,
                 data,
                 index):

        self.data = data
        self.index = index

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                data = GeoDataFrame()
            # Make sure there is an index column
            data["index"] = range(len(data))

        # Add new layer        
        self.mapbox.runjs("./js/line_selector_layer.js", "addLayer", arglist=[self.map_id,
                                                                               data.to_crs(4326),
                                                                               index,
                                                                               self.line_color,
                                                                               self.line_width,
                                                                               self.line_style,
                                                                               self.line_opacity,
                                                                               self.line_color_selected,
                                                                               self.line_width_selected,
                                                                               self.line_style_selected,
                                                                               self.line_opacity_selected,
                                                                               self.hover_param,
                                                                               self.selection_type])

        # if self.mode == "inactive":
        #     self.deactivate()
        if not self.active:
            self.deactivate()

    def set_selected_index(self, index):
        self.mapbox.runjs("/js/line_selector_layer.js", "setSelectedIndex", arglist=[self.map_id, index])


    def activate(self):
        # The line_selector_layer has no setPaintProperties yet.
        return
        self.mapbox.runjs("./js/line_selector_layer.js", "setPaintProperties", arglist=[self.map_id,
                                                                               self.line_color,
                                                                               self.line_width,
                                                                               self.line_style,
                                                                               self.line_opacity,
                                                                               self.line_color_selected,
                                                                               self.line_width_selected,
                                                                               self.line_style_selected,
                                                                               self.line_opacity_selected])
  
    def deactivate(self):
        # The line_selector_layer has no setPaintProperties yet.
        return
        self.mapbox.runjs("./js/line_selector_layer.js", "setPaintProperties", arglist=[self.map_id,
                                                                                         self.line_color_inactive,
                                                                                         self.line_width_inactive,
                                                                                         self.line_style_inactive,
                                                                                         self.line_opacity_inactive])

    # def set_visibility(self, true_or_false):
    #     if true_or_false:
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".line"])
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".circle"])
    #     else:
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".line"])
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".circle"])

    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data, self.index)
        if not self.get_visibility():
            self.set_visibility(False)
