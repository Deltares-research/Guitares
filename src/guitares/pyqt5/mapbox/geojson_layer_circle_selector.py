from .layer import Layer
from geopandas import GeoDataFrame

class GeoJSONLayerCircleSelector(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(self,
                 data,
                 index,
                 legend_title="",
                 crs=None):

        self.data = data
        self.index = index

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                data = GeoDataFrame()

        # Remove existing layer        
        self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id])
        # Add new layer        
        indices = []
        indices.extend(range(len(data)))
        data["index"] = indices
        self.mapbox.runjs("./js/geojson_layer_circle_selector.js", "addLayer", arglist=[self.map_id,
                                                                                        data,
                                                                                        index,
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

    def set_selected_index(self, index):
        self.mapbox.runjs("/js/geojson_layer_circle_selector.js", "setSelectedIndex", arglist=[self.map_id, index])

    def activate(self):
        self.mapbox.runjs("./js/geojson_layer_circle_selector.js", "activate", arglist=[self.map_id,
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
        self.mapbox.runjs("./js/geojson_layer_circle_selector.js", "deactivate", arglist=[self.map_id,
                                                                                        self.line_color_inactive,
                                                                                        self.line_width_inactive,
                                                                                        self.line_style_inactive,
                                                                                        self.line_opacity_inactive,
                                                                                        self.fill_color_inactive,
                                                                                        self.fill_opacity_inactive,
                                                                                        self.circle_radius_inactive,
                                                                                        self.line_color_selected_inactive,
                                                                                        self.fill_color_selected_inactive,
                                                                                        self.circle_radius_selected_inactive])

    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data, self.index)


    # def set_visibility(self, true_or_false):
    #     if true_or_false:
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".fill"])
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".line"])
    #     else:
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".fill"])
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".line"])
