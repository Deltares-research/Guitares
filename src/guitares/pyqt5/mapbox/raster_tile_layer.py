import os

from .layer import Layer
# from geopandas import GeoDataFrame

class RasterTileLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)

        pass

    def set_data(self,
                 data):
        self.data = data
        # check if the string already contains the x, y, z part
        if "{x}" in data:
            url = data
        else:
            url = data + "/{z}/{x}/{y}.png"
        # url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"    
        # Add new layer        
        self.mapbox.runjs("./js/raster_tile_layer.js", "addLayer", arglist=[self.map_id,
                                                                    url])
    def redraw(self):
        # if isinstance(self.data, GeoDataFrame):
        #     self.set_data(self.data)
        if not self.get_visibility():
            self.set_visibility(False)

    def activate(self):
        pass
        # self.mapbox.runjs("./js/line_layer.js", "setPaintProperties", arglist=[self.map_id,
        #                                                                        self.line_color,
        #                                                                        self.line_width,
        #                                                                        self.line_opacity,
        #                                                                        self.fill_color,
        #                                                                        self.fill_opacity,
        #                                                                        self.circle_radius])
  
    def deactivate(self):
        pass
        # self.mapbox.runjs("./js/line_layer.js", "setPaintProperties", arglist=[self.map_id,
        #                                                                        self.line_color_inactive,
        #                                                                        self.line_width_inactive,
        #                                                                        self.line_opacity_inactive,
        #                                                                        self.fill_color_inactive,
        #                                                                        self.fill_opacity_inactive,
        #                                                                        self.circle_radius_inactive])

    # def set_visibility(self, true_or_false):
    #     if true_or_false:
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".line"])
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".circle"])
    #     else:
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".line"])
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".circle"])

