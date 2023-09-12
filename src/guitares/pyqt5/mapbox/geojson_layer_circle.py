from .layer import Layer
from geopandas import GeoDataFrame
from pyogrio import read_dataframe


class GeoJSONLayerCircle(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)

        pass

    def set_data(
        self,
        data,
        hover_property="",
        big_data=False,
    ):
        self.hover_property = hover_property
        self.big_data = big_data

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                data = GeoDataFrame()
            if data.crs != 4326:
                data = data.to_crs(4326)
            self.gdf = data
        else:
            # Read geodataframe from shape file
            self.gdf = read_dataframe(data)

        # Remove existing layer
        self.remove()

        if self.mode == "invisible":
            self.visibility = "none"
        else:
            self.visibility = "visible"

        if not self.big_data:
            # Add new layer
            self.mapbox.runjs(
                "./js/geojson_layer_circle.js",
                "addLayer",
                arglist=[
                    self.map_id,
                    self.gdf,
                    self.hover_property,
                    self.min_zoom,
                    self.line_color,
                    self.line_width,
                    self.line_opacity,
                    self.fill_color,
                    self.fill_opacity,
                    self.circle_radius,
                    self.visibility,
                ],
            )

        self.visible = True
        self.update()

    def update(self):
        if not self.mapbox.zoom:
            return
        if self.mapbox.zoom > self.min_zoom and self.big_data and self.visible:
            coords = self.mapbox.map_extent
            xl0 = coords[0][0]
            xl1 = coords[1][0]
            yl0 = coords[0][1]
            yl1 = coords[1][1]
            # Limits WGS 84
            gdf = self.gdf.cx[xl0:xl1, yl0:yl1]

            # Remove existing layer
            self.remove()

            # Add new layer
            self.mapbox.runjs(
                "./js/geojson_layer_circle.js",
                "addLayer",
                arglist=[
                    self.map_id,
                    gdf,
                    self.hover_property,
                    self.min_zoom,
                    self.line_color,
                    self.line_width,
                    self.line_opacity,
                    self.fill_color,
                    self.fill_opacity,
                    self.circle_radius,
                    self.visibility,
                ],
            )

    def remove(self):
        self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id])

    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data, self.hover_property)

    def activate(self):
        self.mapbox.runjs(
            "./js/geojson_layer_circle.js",
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
        self.mapbox.runjs(
            "./js/geojson_layer_circle.js",
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

    def set_visibility(self, true_or_false):
        if true_or_false:
            self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id])
            self.visible = True
        else:
            self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id])
            self.visible = False
        self.update()
