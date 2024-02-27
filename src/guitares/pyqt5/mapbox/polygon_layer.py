from .layer import Layer
from geopandas import GeoDataFrame


class PolygonLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(
        self,
        data,
    ):

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                data = GeoDataFrame()

        self.data = data

        # Add new layer
        self.mapbox.runjs(
            "./js/simple_polygon_layer.js",
            "addLayer",
            arglist=[
                self.map_id,
                self.data,
                self.line_color,
                self.line_width,
                self.line_opacity,
            ],
        )

    def activate(self):
        self.active = True
        if self.data is None:
            return
        self.mapbox.runjs(
            "/js/simple_polygon_layer.js",
            "activate",
            arglist=[self.map_id, self.line_color],
        )

    def deactivate(self):
        self.active = False
        if self.data is None:
            return
        self.mapbox.runjs(
            "./js/geojson_layer_circle.js",
            "deactivate",
            arglist=[
                self.map_id,
                self.line_color_inactive,
            ],
        )

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
