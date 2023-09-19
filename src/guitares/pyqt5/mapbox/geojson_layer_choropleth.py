from .layer import Layer
from geopandas import GeoDataFrame
from pyogrio import read_dataframe


class GeoJSONLayerChoropleth(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(
        self,
        data,
        hover_property="",
        color_property="",
        scaler=None,
        big_data=False,
        legend_title="",
        unit="",
    ):
        self.hover_property = hover_property
        self.color_property = color_property
        self.scaler = scaler
        self.big_data = big_data
        self.legend_title = legend_title
        self.unit = unit

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

        # Prepare colormap

        if not self.big_data:
            # Add new layer
            self.mapbox.runjs(
                "./js/geojson_layer_choropleth.js",
                "addLayer",
                arglist=[
                    self.map_id,
                    self.gdf,
                    self.min_zoom,
                    self.hover_property,
                    self.color_property,
                    self.line_color,
                    self.line_width,
                    self.line_opacity,
                    self.fill_opacity,
                    self.scaler,
                    self.legend_title,
                    self.unit,
                    self.legend_position
                ],
            )
        self.visible = True
        self.update()

    def update(self):
        if self.big_data and self.visible:
            # Using big data algorithm
            if self.mapbox.zoom > self.min_zoom:
                # Zoomed in
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
                    "./js/geojson_layer_choropleth.js",
                    "addLayer",
                    arglist=[
                        self.map_id,
                        gdf,
                        self.min_zoom,
                        self.hover_property,
                        self.color_property,
                        self.line_color,
                        self.line_width,
                        self.line_opacity,
                        self.fill_opacity,
                        self.scaler,
                        self.legend_title,
                        self.unit,
                        self.legend_position
                    ],
                )
            else:
                # Zoomed out
                # Choropleths are automatically invisible, but legend is not         
                self.mapbox.runjs("/js/main.js", "hideLegend", arglist=[self.map_id])



    def activate(self):
        self.active = True
        self.mapbox.runjs(
            "./js/geojson_layer_choropleth.js",
            "activate",
            arglist=[
                self.map_id,
                self.line_color,
                self.fill_color,
                self.line_color_selected,
                self.fill_color_selected,
            ],
        )

    def deactivate(self):
        self.active = False
        self.mapbox.runjs(
            "./js/geojson_layer_choropleth.js",
            "deactivate",
            arglist=[
                self.map_id,
                self.line_color_inactive,
                self.line_width_inactive,
                self.line_style_inactive,
                self.line_opacity_inactive,
                self.fill_color_inactive,
                self.fill_opacity_inactive,
                self.line_color_selected_inactive,
                self.fill_color_selected_inactive,
            ],
        )

    def redraw(self):
        if isinstance(self.gdf, GeoDataFrame):
            self.set_data(self.gdf, self.hover_property, self.color_property)
        if not self.visible:
            self.hide()

    def clear(self):
        self.active = False
        self.remove()

    def remove(self):
        self.mapbox.runjs(
            "./js/main.js", "removeLayer", arglist=[self.map_id + ".fill"]
        )
        self.mapbox.runjs(
            "./js/main.js", "removeLayer", arglist=[self.map_id + ".line"]
        )
        self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id])

    def set_visibility(self, true_or_false):
        if true_or_false:
            self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id])
            self.mapbox.runjs(
                "/js/main.js", "showLayer", arglist=[self.map_id + ".fill"]
            )
            self.mapbox.runjs(
                "/js/main.js", "showLayer", arglist=[self.map_id + ".line"]
            )
            self.visible = True
        else:
            self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id])
            self.mapbox.runjs(
                "/js/main.js", "hideLayer", arglist=[self.map_id + ".fill"]
            )
            self.mapbox.runjs(
                "/js/main.js", "hideLayer", arglist=[self.map_id + ".line"]
            )
            self.visible = False
        self.update()
