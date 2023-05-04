from .layer import Layer
from geopandas import GeoDataFrame


class GeoJSONLayerHeatmap(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(self, data, density_property=""):
        self.data = data
        self.density_property = density_property

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                data = GeoDataFrame()

        # Remove existing layer
        self.remove()

        # Add new layer
        self.mapbox.runjs(
            "./js/geojson_layer_heatmap.js",
            "addLayer",
            arglist=[
                self.map_id,
                data,
                self.max_zoom,
                density_property,
            ],
        )

    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data, self.density_property)
        if not self.visible:
            self.hide()

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def clear(self):
        self.active = False
        self.remove()

    def remove(self):
        self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id])

    def update(self):
        pass

    def set_visibility(self, true_or_false):
        if true_or_false:
            self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id])
        else:
            self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id])
