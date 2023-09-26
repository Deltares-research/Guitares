import matplotlib.colors as mcolors

class Layer:
    def __init__(self, mapbox, id, map_id, **kwargs):
        self.mapbox    = mapbox
        self.id        = id
        self.map_id    = map_id
        self.map_ids   = [map_id]
        self.visible   = True
        self.active    = True
        self.type      = "container"
        self.layer     = {}
        self.parent    = None
#        self.mode      = "active"
        self.data      = None
        self.index     = None
        self.select    = None
        self.crs       = 4326
        self.hover_property = "name"
        self.color_property = "value"
        self.legend_position = "bottom-right" # Options are "top-left", "top-right", "bottom-left", "bottom-right"
        # Active paint properties
        self.line_color     = "dodgerblue"
        self.line_width     = 2
        self.line_style     = "-"
        self.line_opacity   = 1.0
        self.fill_color     = "dodgerblue"
        self.fill_opacity   = 1.0
        self.circle_radius  = 4
        # Inactive paint properties
        self.line_color_inactive    = "lightgrey"
        self.line_width_inactive    = 2
        self.line_style_inactive    = "-"
        self.line_opacity_inactive  = 1.0
        self.fill_color_inactive    = "lightgrey"
        self.fill_opacity_inactive  = 0.0
        self.circle_radius_inactive = 2
        # Selected paint properties 
        self.line_color_selected    = "dodgerblue"
        self.line_width_selected    = 2
        self.line_style_selected    = "-"
        self.line_opacity_selected  = 1.0
        self.fill_color_selected    = "red"
        self.fill_opacity_selected  = 1.0
        self.circle_radius_selected = 5
        # Selected inactive paint properties
        self.line_color_selected_inactive    = "lightgrey"
        self.line_width_selected_inactive    = 2
        self.line_style_selected_inactive    = "-"
        self.line_opacity_selected_inactive  = 1.0
        self.fill_color_selected_inactive    = "lightgrey"
        self.fill_opacity_selected_inactive  = 0.0
        self.circle_radius_selected_inactive = 2

        self.selection_type = "single"
        self.min_zoom = 0
        self.max_zoom = 22
        self.zoom_switch = 999
        self.decimals = 1
        self.big_data = False

        # Cyclone track layer
        self.show_icons = True

        # Determine which main.js file to use 
        if type(self.mapbox).__name__ == "MapBox":
            # Regular mapbox
            self.main_js = "/js/main.js"
            self.side    = "main"
        elif type(self.mapbox).__name__ == "MapBoxCompare":
            # Compare mapbox
            self.main_js = "/js/compare.js"
            self.side = "a"

        # Set attributes based on kwargs 
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Convert colors to hex
        if self.line_color != "transparent": 
            self.line_color = mcolors.to_hex(self.line_color)
        if self.fill_color != "transparent": 
            self.fill_color = mcolors.to_hex(self.fill_color)
        if self.line_color_inactive != "transparent": 
            self.line_color_inactive = mcolors.to_hex(self.line_color_inactive)
        if self.fill_color_inactive != "transparent": 
            self.fill_color_inactive = mcolors.to_hex(self.fill_color_inactive)
        if self.line_color_selected != "transparent": 
            self.line_color_selected = mcolors.to_hex(self.line_color_selected)
        if self.fill_color_selected != "transparent": 
            self.fill_color_selected = mcolors.to_hex(self.fill_color_selected)
        if self.line_color_selected_inactive != "transparent": 
            self.line_color_selected_inactive = mcolors.to_hex(self.line_color_selected_inactive)
        if self.fill_color_selected_inactive != "transparent": 
            self.fill_color_selected_inactive = mcolors.to_hex(self.fill_color_selected_inactive)

    def add_layer(self, layer_id, type=None, **kwargs):

        if layer_id in self.layer:
            # Layer already exists
            return self.layer[layer_id]

        map_id = self.map_id + "." + layer_id

        if type == None:

            # Add containing layer
            self.layer[layer_id] = Layer(self.mapbox, layer_id, map_id)
#            self.layer[layer_id] = Layer(self.mapbox, layer_id, map_id, mode=mode)
            self.layer[layer_id].parent = self
            return self.layer[layer_id]
        
        else:

            if self.type != "container":
                print("Error! Can not add layer to layer of type : " + self.type)
                return None

            if type == "circle_selector":
                from .geojson_layer_circle_selector import GeoJSONLayerCircleSelector
                self.layer[layer_id] = GeoJSONLayerCircleSelector(self.mapbox, layer_id, map_id, **kwargs)

            elif type == "polygon_selector":
                from .geojson_layer_polygon_selector import GeoJSONLayerPolygonSelector
                self.layer[layer_id] = GeoJSONLayerPolygonSelector(self.mapbox, layer_id, map_id, **kwargs)

            elif type == "line_selector":
                from .geojson_layer_line_selector import GeoJSONLayerLineSelector
                self.layer[layer_id] = GeoJSONLayerLineSelector(self.mapbox, layer_id, map_id, **kwargs)

            elif type == "choropleth":
                from .geojson_layer_choropleth import GeoJSONLayerChoropleth
                self.layer[layer_id] = GeoJSONLayerChoropleth(self.mapbox, layer_id, map_id, **kwargs)
            
            elif type == "heatmap":
                from .geojson_layer_heatmap import GeoJSONLayerHeatmap
                self.layer[layer_id] = GeoJSONLayerHeatmap(self.mapbox, layer_id, map_id, **kwargs)

            elif type == "circle":
                from .geojson_layer_circle import GeoJSONLayerCircle
                self.layer[layer_id] = GeoJSONLayerCircle(self.mapbox, layer_id, map_id, **kwargs)
            
            elif type == "line":
                from .geojson_layer_line import GeoJSONLayerLine
                self.layer[layer_id] = GeoJSONLayerLine(self.mapbox, layer_id, map_id, **kwargs)

            elif type == "draw":
                from .draw_layer import DrawLayer
                self.layer[layer_id] = DrawLayer(self.mapbox, layer_id, map_id, **kwargs)

            elif type == "image":
                from .image_layer import ImageLayer
                self.layer[layer_id] = ImageLayer(self.mapbox, layer_id, map_id, **kwargs)

            elif type == "raster":
                from .raster_layer import RasterLayer
                self.layer[layer_id] = RasterLayer(self.mapbox, layer_id, map_id, **kwargs)

            elif type == "raster_from_tiles":
                from .raster_from_tiles_layer import RasterFromTilesLayer
                self.layer[layer_id] = RasterFromTilesLayer(self.mapbox, layer_id, map_id, **kwargs)

            elif type == "deck_geojson":
                from .deck_geojson_layer import DeckGeoJSONLayer
                self.layer[layer_id] = DeckGeoJSONLayer(self.mapbox, layer_id, map_id, **kwargs)

            elif type == "datashader_choropleth":
                from .datashader_choropleth_layer import DatashaderChoroplethLayer
                self.layer[layer_id] = DatashaderChoroplethLayer(self.mapbox, layer_id, map_id, **kwargs)
            elif type == "cyclone_track":
                from .cyclone_track_layer import CycloneTrackLayer
                self.layer[layer_id] = CycloneTrackLayer(self.mapbox, layer_id, map_id, **kwargs)

            else:
                print("Error! Layer type " + self.type + " not recognized!")
                return None

            self.layer[layer_id].type = type
            self.layer[layer_id].parent = self
#            self.layer[layer_id].mode = mode

            return self.layer[layer_id]
 
    def layer_added(self):
        # This function is called after a layer is added to the map (is it always called? not right now)
        if not self.visible:
            self.hide()
        if not self.active:
            self.deactivate()

    def update(self):
        # This method is called when map zoom or pan is changed
        # For certain layers, this method is overridden in the subclass
        pass

    def delete(self):
        # Delete this layer and all nested layers from map
        if self.layer:
            # Container layer
            layers = list_layers(self.layer)
            for layer in layers:
                layer.delete()
        else:        
            self.delete_from_map()

        # Remove layer from layer dict
        if self.parent:
            self.parent.layer.pop(self.id)
        else:
            self.mapbox.layer.pop(self.id)

    def clear(self):
        # Clear this layer and all nested layers from map
        if self.layer:
            # Container layer
            layers = list_layers(self.layer)
            for layer in layers:
                layer.clear()
        else:        
            self.delete_from_map()
            self.data = None

    def delete_from_map(self):
        self.mapbox.runjs(self.main_js, "removeLayer", arglist=[self.map_id, self.side])

    def show(self):
        self.visible = True
        self.set_visibility(True)

    def hide(self):
        self.visible = False
        self.set_visibility(False)

    def set_visibility(self, true_or_false):
        if self.layer:
            # Container layer
            # Make a list of all layers
            layers = list_layers(self.layer)
            for layer in layers:
                layer.set_visibility(true_or_false)
        else:
            # Data layer
            if true_or_false and self.visible:
                self.mapbox.runjs(self.main_js, "showLayer", arglist=[self.map_id, self.side])
            else:
                self.mapbox.runjs(self.main_js, "hideLayer", arglist=[self.map_id, self.side])

    def get_visibility(self):
        # Loop up through the layer hierarchy to determine if the layer is visible
        if self.visible:
            if self.parent:
                return self.parent.get_visibility()
            else:
                return True
        else:
            return False    

    def activate(self):
        # Only called for layers that do not have a activate function in the subclass
        self.active = True
        if self.layer:
            self.set_activity(True)

    def deactivate(self):
        # Only called for layers that do not have a deactivate function in the subclass
        self.active = False    
        if self.layer:
            self.set_activity(False)

    def set_activity(self, true_or_false):
        if self.layer:
            # Container layer
            # Make a list of all layers
            layers = list_layers(self.layer)
            for layer in layers:
                layer.set_activity(true_or_false)
        else:
            # Data layer
            if true_or_false and self.activate:
                self.activate()
            else:
                self.deactivate()

    def get(self, layer_id):
        if layer_id in self.layer:
            return self.layer[layer_id]
        else:
            return None

    # def set_mode(self, mode):
    #     # Make a list of all layers
    #     if self.layer:
    #         # Container layer
    #         self.mode = mode
    #         layers = list_layers(self.layer)
    #         for layer in layers:                
    #             layer.set_mode(mode)
    #     else:
    #         # Only change if mode has changed
    #         if self.mode != mode:
    #             if mode == "active":
    #                 self.visible = True
    #                 self.mapbox.runjs(self.main_js, "showLayer", arglist=[self.map_id, self.side])
    #                 self.activate()
    #             elif mode == "inactive":
    #                 self.visible = True
    #                 self.mapbox.runjs(self.main_js, "showLayer", arglist=[self.map_id, self.side])
    #                 self.deactivate()
    #             else: # Invisible   
    #                 self.visible = False
    #                 self.mapbox.runjs(self.main_js, "hideLayer", arglist=[self.map_id, self.side])
    #         self.mode = mode

    def redraw(self):
        # This method is called when the layers style is changed
        # For most layers, this method is overridden in the subclass
        pass

def list_layers(layer_dict, layer_type="all", layer_list=None):
    if not layer_list:
        layer_list = []
    for layer_name in layer_dict:
        layer = layer_dict[layer_name]
        if layer_type != "all":
            if layer.type == layer_type:
                layer_list.append(layer)
        else:
            layer_list.append(layer)

        if layer.layer:
            layer_list = list_layers(layer.layer,
                                     layer_list=layer_list,
                                     layer_type=layer_type)
    return layer_list

def find_layer_by_id(layer_id, layer_dict, layer_type="all", layer_list=None):
    layer_list = list_layers(layer_dict)
    for layer in layer_list:
        if layer.map_id == layer_id:
            return layer
