# from .image_layer import ImageLayer
# from .deck_tile_layer import DeckTileLayer

class Layer:
    def __init__(self, mapbox, id, map_id):
        self.mapbox    = mapbox
        self.id        = id
        self.map_id    = map_id
        self.type      = "container"
        self.layer     = {}
        self.parent    = None

    def update(self):
        pass

    def delete(self):
        # Delete this layer and all nested layers from map
        self.delete_from_map()

        # Remove layer from layer dict
        self.parent.layer.pop(self.id)

    def delete_from_map(self):
        self.mapbox.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])

    def clear(self):
        pass

    def get(self, layer_id):
        if layer_id in self.layer:
            return self.layer[layer_id]
        else:
            return None

    def add_layer(self, layer_id):
        # Add containing layer
        map_id = self.map_id + "." + layer_id
        self.layer[layer_id] = Layer(self.mapbox, layer_id, map_id)
        self.layer[layer_id].parent = self
        return self.layer[layer_id]

    def add_draw_layer(self, layer_id, **kwargs):
        from .draw_layer import DrawLayer
        if self.type != "container":
            print("Error! Can not add draw layer to layer of type : " + self.type)
            return None
        map_id = self.map_id + "." + layer_id
        if layer_id not in self.layer:
            self.layer[layer_id] = DrawLayer(self.mapbox, layer_id, map_id, **kwargs)
            self.layer[layer_id].parent = self
        return self.layer[layer_id]

    def add_raster_layer(self, layer_id, data=None):
        from .raster_layer import RasterLayer
        map_id = self.map_id + "." + layer_id
        if self.type != "container":
            print("Error! Can not add raster layer to layer of type : " + self.type)
            return None
        if layer_id not in self.layer:
            self.layer[layer_id] = RasterLayer(self.mapbox, layer_id, map_id)
            self.layer[layer_id].parent = self
        return self.layer[layer_id]

    def add_geojson_layer(self, layer_id, **kwargs):
        from .geojson_layer import GeoJSONLayer
        map_id = self.map_id + "." + layer_id
        if self.type != "container":
            print("Error! Can not add geojson_layer to layer of type : " + self.type)
            return None
        if layer_id not in self.layer:
            self.layer[layer_id] = GeoJSONLayer(self.mapbox, layer_id, map_id, **kwargs)
            self.layer[layer_id].parent = self
        return self.layer[layer_id]

    def add_deck_geojson_layer(self, layer_id, **kwargs):
        from .deck_geojson_layer import DeckGeoJSONLayer
        map_id = self.map_id + "." + layer_id
        if self.type != "container":
            print("Error! Can not add deck_geojson_layer to layer of type : " + self.type)
            return None
        if layer_id not in self.layer:
            self.layer[layer_id] = DeckGeoJSONLayer(self.mapbox, layer_id, map_id, **kwargs)
            self.layer[layer_id].parent = self
        return self.layer[layer_id]

    def show(self):
        self.set_visibility(True)

    def hide(self):
        self.set_visibility(False)

    def set_visibility(self, true_or_false):
        # Make a list of all layers
        if self.layer:
            # Container layer
            layers = list_layers(self.layer)
            for layer in layers:
                layer.set_visibility(true_or_false)
        else:
            if true_or_false:
                self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id])
            else:
                self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id])

    def set_mode(self, mode):
        # Make a list of all layers
        if self.layer:
            # Container layer
            layers = list_layers(self.layer)
            for layer in layers:
                layer.set_mode(mode)
        else:
            if mode == "active" or mode == "inactive":
                js_string = "import('./js/main.js').then(module => {module.showLayer('" + self.map_id + "')});"
            else:
                js_string = "import('./js/main.js').then(module => {module.hideLayer('" + self.map_id + "')});"
            self.mapbox.view.page().runJavaScript(js_string)


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

    #     # Now add the layer
    #     if type == "draw":
    #         layer = DrawLayer(self, layer_id, create=create, modify=modify, select=select)
    #     elif type == "image":
    #         layer = ImageLayer(self, layer_id)
    #     elif type == "raster":
    #         layer = RasterLayer(self, layer_id)
    #     elif type == "deckgeojson":
    #         layer = DeckGeoJSONLayer(self, layer_id, data=data)
    #     elif type == "decktile":
    #         layer = DeckTileLayer(self, layer_id, data=data)


    # def add_marker_layer(self,
    #                      collection,
    #                      marker_file=None,
    #                      layer_name=None,
    #                      layer_group_name=None):
    #
    #     self.id_counter += 1
    #     id_string = str(self.id_counter)
    #     layer = Layer(name=layer_name, type="image")
    #     layer.id = id_string
    #     layer_group = self.find_layer_group(layer_group_name)
    #     layer_group[layer_name] = layer
    #     geojs = geojson.dumps(collection)
    #     js_string = "import('/main.js').then(module => {module.addMarkerLayer(" + geojs + ",'" + marker_file + "','" + id_string + "','"+ layer_name + "','" + layer_group_name + "')});"
    #     self.view.page().runJavaScript(js_string)
