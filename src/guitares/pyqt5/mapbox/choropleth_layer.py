from .layer import Layer
from geopandas import GeoDataFrame
from pyogrio import read_dataframe


class ChoroplethLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(
        self, data, color_by_attribute: dict = None, legend_items: list = None, 
    ):
        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                data = GeoDataFrame()
            if data.crs != 4326:
                data = data.to_crs(4326)
        else:
            # Read geodataframe from shape file
            data = read_dataframe(data)

        self.data = data
        # self.visible = True

        if not self.big_data:
            if color_by_attribute is None:
                # Add new layer
                self.mapbox.runjs(
                    "./js/choropleth_layer.js",
                    "addLayer",
                    arglist=[
                        self.map_id,
                        self.data,
                        self.min_zoom,
                        self.hover_property,
                        self.color_property,
                        self.line_color,
                        self.line_width,
                        self.line_opacity,
                        self.fill_opacity,
                        self.legend_title,
                        self.unit,
                        self.legend_position,
                        self.side,
                        self.bins,
                        self.colors,
                        self.color_labels,
                    ],
                )
            elif isinstance(color_by_attribute, dict) and isinstance(
                legend_items, list
            ):
                # Color by attribute
                self.mapbox.runjs(
                    "./js/polygon_layer_custom.js",
                    "addLayer",
                    arglist=[
                        self.map_id,
                        self.data,
                        self.hover_property,
                        self.min_zoom,
                        color_by_attribute,
                        legend_items,
                        self.legend_position,
                        self.legend_title,
                    ],
                )
            elif isinstance(color_by_attribute, dict
            ):
                # Color by attribute
                self.mapbox.runjs(
                    "./js/polygon_layer_additional_attr.js",
                    "addLayer",
                    arglist=[
                        self.map_id,
                        self.data,
                        self.hover_property,
                        self.min_zoom,
                        color_by_attribute,
                        legend_items,
                        self.legend_position,
                        self.legend_title,
                    ],
                )
        else:
            self.update()

    def update(self):
        if self.data is None:
            return
        if len(self.data) == 0:
            # Empty GeoDataFrame
            return
        # Only need to update this layer if it use big data and is visible
        if self.big_data and self.get_visibility():
            if self.mapbox.zoom > self.min_zoom:
                # Zoomed in
                coords = self.mapbox.map_extent
                xl0 = coords[0][0]
                xl1 = coords[1][0]
                yl0 = coords[0][1]
                yl1 = coords[1][1]
                # Limits WGS 84
                gdf = self.data.cx[xl0:xl1, yl0:yl1]
                # Remove existing layer
                # Add new layer
                self.mapbox.runjs(
                    "./js/choropleth_layer.js",
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
                        self.legend_title,
                        self.unit,
                        self.legend_position,
                        self.side,
                        self.bins,
                        self.colors,
                        self.color_labels,
                    ],
                )
            else:
                # Zoomed out
                # Choropleths are automatically invisible, but legend is not
                self.mapbox.runjs(self.main_js, "hideLegend", arglist=[self.map_id])

    def activate(self):
        self.active = True
        self.mapbox.runjs(
            "./js/choropleth_layer.js",
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
            "./js/choropleth_layer.js",
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
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)
        if not self.get_visibility():
            self.set_visibility(False)
