from .layer import Layer
from geopandas import GeoDataFrame

class PolygonSelectorLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(self,
                 data,
                 index = None
                 ):
       
        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                data = GeoDataFrame()

        indices = []
        indices.extend(range(len(data)))
        data["index"] = indices
        
        self.data = data 
        
        if isinstance(index, int):
            self.index = [index]
        elif not index and self.selection_type=="multiple":
            self.index = None  
        elif not index and self.selection_type=="single":
            self.index = [indices[0]]
        else:
            self.index = index
            
        # Add new layer
        self.mapbox.runjs("./js/polygon_selector_layer.js", "addLayer", arglist=[self.map_id,
                                                                                         self.data,
                                                                                         self.index,
                                                                                         self.hover_property,
                                                                                         self.line_color,
                                                                                         self.line_width,
                                                                                         self.line_opacity,
                                                                                         self.fill_color,
                                                                                         self.fill_opacity,
                                                                                         self.selection_type])

    def set_selected_index(self, index):
        self.index = index
        self.mapbox.runjs("/js/polygon_selector_layer.js", "setSelectedIndex", arglist=[self.map_id, index])

    # Probably should not have a separate function for this
    # Can also done with layer.hover_property = "name" and then layer.redraw() 
    def set_hover_property(self, hover_property):
        data = self.data
        index = self.index
        self.hover_property = hover_property
        self.set_data(data, index)

    def select_by_index(self, index):
        self.mapbox.runjs("/js/polygon_selector_layer.js", "selectByIndex", arglist=[self.map_id, index])

    def select_by_id(self, id):
        self.mapbox.runjs("/js/polygon_selector_layer.js", "selectById", arglist=[self.map_id, id])

    def activate(self):
        self.active = True
        if self.data is None:
            return
        self.mapbox.runjs("/js/polygon_selector_layer.js", "activate", arglist=[self.map_id,
                                                                                         self.line_color,
                                                                                         self.fill_color,
                                                                                         self.line_color_selected,
                                                                                         self.fill_color_selected])
  
    def deactivate(self):
        self.active = False
        if self.data is None:
            return
        self.mapbox.runjs("./js/geojson_layer_circle_selector.js", "deactivate", arglist=[self.map_id,
                                                                                          self.line_color_inactive,
                                                                                          self.line_width_inactive,
                                                                                          self.line_style_inactive,
                                                                                          self.line_opacity_inactive,
                                                                                          self.fill_color_inactive,
                                                                                          self.fill_opacity_inactive,
                                                                                          self.line_color_selected_inactive,
                                                                                          self.fill_color_selected_inactive])

    def redraw(self):
        # Called when the map style is changed
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data, self.index)
        if not self.get_visibility():
            self.set_visibility(False)

    # def activate(self):
    #     self.active = True

    # def deactivate(self):
    #     self.active = False

    # def clear(self):
    #     self.active = False
    #     self.remove()

    # def remove(self):
    #     self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id + ".fill"])
    #     self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id + ".line"])
    #     self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id])

    # def update(self):
    #     pass

    # def set_visibility(self, true_or_false):
    #     if true_or_false and self.visible:
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".fill"])
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".line"])
    #     else:
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".fill"])
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".line"])
