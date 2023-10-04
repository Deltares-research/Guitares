from .layer import Layer
from geopandas import GeoDataFrame
from pyogrio import read_dataframe


class CircleLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(self, data):
        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                return
            if data.crs != 4326:
                data = data.to_crs(4326)
        else:
            # Read geodataframe from shape file
            data = read_dataframe(data)

        self.data = data

        if not self.big_data:
            # Add new layer
            self.mapbox.runjs(
                "./js/circle_layer.js",
                "addLayer",
                arglist=[
                    self.map_id,
                    self.data,
                    self.hover_properties,
                    self.min_zoom,
                    self.line_color,
                    self.line_width,
                    self.line_opacity,
                    self.fill_color,
                    self.fill_opacity,
                    self.circle_radius,
                ],
            )

        else:
            self.update()

    def update(self):
        if not self.mapbox.zoom:
            return
        if self.data is None:
            return
        if len(self.data) == 0:
            # Empty GeoDataFrame
            return
        if self.big_data and self.visible:
            if self.mapbox.zoom > self.min_zoom:
                coords = self.mapbox.map_extent
                xl0 = coords[0][0]
                xl1 = coords[1][0]
                yl0 = coords[0][1]
                yl1 = coords[1][1]
                # Limits WGS 84
                gdf = self.data.cx[xl0:xl1, yl0:yl1]
                # Add new layer
                self.mapbox.runjs(
                    "./js/circle_layer.js",
                    "addLayer",
                    arglist=[
                        self.map_id,
                        gdf,
                        self.hover_properties,
                        self.min_zoom,
                        self.line_color,
                        self.line_width,
                        self.line_opacity,
                        self.fill_color,
                        self.fill_opacity,
                        self.circle_radius,
                    ],
                )
            else:
                # Zoomed out
                # Choropleths are automatically invisible, but legend is not
                self.mapbox.runjs(self.main_js, "hideLegend", arglist=[self.map_id])

    def activate(self):
        self.active = True
        self.mapbox.runjs(
            "./js/circle_layer.js",
            "setPaintProperties",
            arglist=[
                self.map_id,
                self.line_color,
                self.line_width,
                self.line_opacity,
                self.fill_color,
                self.fill_opacity,
                self.circle_radius,
            ],
        )

    def deactivate(self):
        self.active = False
        self.mapbox.runjs(
            "./js/circle_layer.js",
            "setPaintProperties",
            arglist=[
                self.map_id,
                self.line_color_inactive,
                self.line_width_inactive,
                self.line_opacity_inactive,
                self.fill_color_inactive,
                self.fill_opacity_inactive,
                self.circle_radius_inactive,
            ],
        )

    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)
        if not self.get_visibility():
            self.hide()
