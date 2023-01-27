from .layer import Layer

class DeckTileLayer(Layer):
    def __init__(self, mapbox, id, map_id, data=None):
        super().__init__(mapbox, id, map_id)
        self.active = False
        self.type   = "decktile"

        data_string = "[]"
        if data:
            # Data is provided
            if isinstance(data, str):
                # Must be a name of file that sits in server folder
                data_string = "'" + data + "'"
            else:
                # Must be
                data_string = geojson.dumps(data)

        js_string = "import('js/deck_tile_layer.js').then(module => {module.addLayer('" + self.map_id + "', " + data_string + " )});"
        self.mapbox.view.page().runJavaScript(js_string)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


    def clear(self):
        self.active = False
        js_string = "import('js/main.js').then(module => {module.removeLayer('" + self.id + "')});"
        self.mapbox.view.page().runJavaScript(js_string)

    def update(self):
        print("Updating image layer")

    def set_data(self,
                 data,
                 legend_title="",
                 crs=None):

        # if not crs:
        #     src_crs = "EPSG:4326"
        # else:
        #     src_crs = "EPSG:" + crs.epsg

        data_string = "[]"
        if data:
            data_string = "'" + data + "'"

        js_string = "import('js/deck_geojson_layer.js').then(module => {module.setData('" + self.id + "'," + data_string + ")});"
        self.mapbox.view.page().runJavaScript(js_string)
