from .layer import Layer
from geopandas import GeoDataFrame

class CircleSelectorLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(self,
                 data,
                 index,
                 crs=None):

        self.data = data
        self.index = index

        # # Remove existing layer
        # self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id])

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                return

        indices = []
        indices.extend(range(len(data)))
        data["index"] = indices

        # Add new layer
        self.mapbox.runjs("./js/circle_selector_layer.js", "addLayer", arglist=[self.map_id,
                                                                                        data.to_crs(4326),
                                                                                        index,
                                                                                        self.hover_property,
                                                                                        self.line_color,
                                                                                        self.line_width,
                                                                                        self.line_style,
                                                                                        self.line_opacity,
                                                                                        self.fill_color,
                                                                                        self.fill_opacity,
                                                                                        self.circle_radius,
                                                                                        self.line_color_selected,
                                                                                        self.fill_color_selected,
                                                                                        self.circle_radius_selected,
                                                                                        self.selection_type])

    def select_by_index(self, index):
        self.mapbox.runjs("/js/circle_selector_layer.js", "selectByIndex", arglist=[self.map_id, index])

    def select_by_id(self, id):
        self.mapbox.runjs("/js/circle_selector_layer.js", "selectById", arglist=[self.map_id, id])

    def activate(self):
        if self.data is None:
            return
        elif len(self.data) == 0:
            return
        self.mapbox.runjs("./js/circle_selector_layer.js", "activate", arglist=[self.map_id,
                                                                                        self.line_color,
                                                                                        self.line_width,
                                                                                        self.line_style,
                                                                                        self.line_opacity,
                                                                                        self.fill_color,
                                                                                        self.fill_opacity,
                                                                                        self.circle_radius,
                                                                                        self.line_color_selected,
                                                                                        self.fill_color_selected,
                                                                                        self.circle_radius_selected])
  
    def deactivate(self):
        if self.data is None:
            return
        elif len(self.data) == 0:
            return
        self.mapbox.runjs("./js/circle_selector_layer.js", "deactivate", arglist=[self.map_id,
                                                                                        self.line_color_inactive,
                                                                                        self.line_width_inactive,
                                                                                        self.line_style_inactive,
                                                                                        self.line_opacity_inactive,
                                                                                        self.fill_color_inactive,
                                                                                        self.fill_opacity_inactive,
                                                                                        self.circle_radius_inactive,
                                                                                        self.line_color_inactive,
                                                                                        self.fill_color_inactive,
                                                                                        self.circle_radius_inactive])

    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data, self.index)
        if not self.get_visibility:
            self.set_visibility(False)
