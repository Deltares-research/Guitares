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


def find_layer_by_id(layer_id, layer_dict):
    layer_list = list_layers(layer_dict)
    for layer in layer_list:
        if layer.map_id == layer_id:
            return layer
