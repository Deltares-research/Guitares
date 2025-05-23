from .layer import Layer
from geopandas import GeoDataFrame


class PolygonLayer(Layer):
    def __init__(self, map, id, map_id, **kwargs):
        super().__init__(map, id, map_id, **kwargs)
        pass

    def set_data(
        self,
        data,
        index=None,
    ):
        # Index is not used, but is kept for consistency with polygon_selector_layer

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                data = GeoDataFrame()

        self.data = data

        # Add new layer
        self.map.runjs(
            "/js/simple_polygon_layer.js",
            "addLayer",
            arglist=[
                self.map_id,
                self.data.to_crs(4326),
                self.line_color,
                self.line_width,
                self.line_opacity,
                self.line_style,
            ],
        )

    def activate(self):
        self.active = True
        if self.data is None:
            return
        self.map.runjs(
            "/js/simple_polygon_layer.js",
            "activate",
            arglist=[self.map_id, self.line_color],
        )

    def deactivate(self):
        self.active = False
        if self.data is None:
            return
        self.map.runjs(
            "/js/geojson_layer_circle.js", # WTF is this?
            "deactivate",
            arglist=[
                self.map_id,
                self.line_color_inactive,
            ],
        )

    def redraw(self):
        # Called when the map style is changed
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)
        if not self.get_visibility():
            self.set_visibility(False)