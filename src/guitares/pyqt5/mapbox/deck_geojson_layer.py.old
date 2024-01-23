import geojson
import os
from geopandas import GeoDataFrame

from .layer import Layer

class DeckGeoJSONLayer(Layer):
    def __init__(self, mapbox, id, map_id, data=None, file_name=None, use_file=True, **kwargs):
        super().__init__(mapbox, id, map_id)
        pass
#        self.active = False
#        self.type   = "deckgeojson"

        # if isinstance(data, GeoDataFrame):
        #     # Data is GeoDataFrame
        #     if use_file:
        #         if not file_name:
        #             file_name = id + ".geojson"
        #         with open(os.path.join(self.mapbox.server_path, "overlays", file_name), "w") as f:
        #             f.write(data.to_json())
        #         data = "./overlays/" + file_name
        #     else:
        #         data = data.to_json()
        # else:
        #     data = []

#        self.mapbox.runjs("./js/deck_geojson_layer.js", "addLayer", arglist=[self.map_id, data])

        # data_string = "[]"
        # if data is not None:
        #     # Data is provided
        #     if isinstance(data, str):
        #         # Must be a name of file that sits in server folder
        #         data_string = "'" + data + "'"
        #     else:
        #         # Must be
        #         data_string = geojson.dumps(data)
        #
        # js_string = "import('./js/deck_geojson_layer.js').then(module => {module.addLayer('" + self.map_id + "', " + data_string + " )});"
        # self.mapbox.view.page().runJavaScript(js_string)

    def activate(self):
        pass

    def deactivate(self):
        pass


    def clear(self):
        pass
        # self.active = False
        # js_string = "import('./js/main.js').then(module => {module.removeLayer('" + self.map_id + "')});"
        # self.mapbox.view.page().runJavaScript(js_string)

    def update(self):
        pass
#        print("Updating Deck GeoJSON layer")

    def set_data(self,
                 data,
                 legend_title="",
                 crs=None):

        # Remove existing layer        
        self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id])

        # Assuming data is GeoDataFrame
        file_name = "_deck.geojson"
        with open(os.path.join(self.mapbox.server_path, "_deck.geojson"), "w") as f:
            f.write(data.to_crs(4326).to_json())
        data = "./" + file_name

        self.mapbox.runjs("./js/deck_geojson_layer.js", "addLayer", arglist=[self.map_id, data])

        # # Assuming data is GeoDataFrame
        # file_name = "_deck.geojson"
        # with open(os.path.join(self.mapbox.server_path, "_deck.geojson"), "w") as f:
        #     f.write(data.to_json())
        # data = "./" + file_name

        # self.mapbox.runjs("/js/deck_geojson_layer.js", "setData", arglist=[self.map_id, data])

        # # if not crs:
        # #     src_crs = "EPSG:4326"
        # # else:
        # #     src_crs = "EPSG:" + crs.epsg
        #
        # data_string = "[]"
        # if data:
        #     data_string = data
        #     data_string = "'" + data + "'"
        #
        # js_string = "import('./js/deck_geojson_layer.js').then(module => {module.setData('" + self.map_id + "'," + data_string + ")});"
        # self.mapbox.view.page().runJavaScript(js_string)
