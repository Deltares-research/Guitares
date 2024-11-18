from .layer import Layer
from geopandas import GeoDataFrame
from pyogrio import read_dataframe


class CircleLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        self.color_by_attribute = dict()
        self.legend_items = list()
        pass

    def set_data(
        self, data, color_by_attribute: dict = dict(), legend_items: list = []
    ):
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

        self.color_by_attribute = color_by_attribute
        self.legend_items = legend_items
        self.data = data
        
        self.unit = getattr(self, 'unit', '')
        
        if not self.big_data:
            if len(self.color_by_attribute) == 0:
                # Add new layer
                #TODO: take unit info from settings.toml
                self.mapbox.runjs(
                    "./js/circle_layer.js",
                    "addLayer",
                    arglist=[
                        self.map_id,
                        self.data,
                        self.hover_property,
                        self.min_zoom,
                        self.line_color,
                        self.line_width,
                        self.line_opacity,
                        self.fill_color,
                        self.fill_opacity,
                        self.circle_radius,
                        self.unit
                    ],
                )
            elif len(self.color_by_attribute) > 0:
                # Color by attribute
                self.mapbox.runjs(
                    "./js/circle_layer_custom.js",
                    "addLayer",
                    arglist=[
                        self.map_id,
                        self.data,
                        self.hover_property,
                        self.unit,
                        self.min_zoom,
                        self.color_by_attribute,
                        self.legend_items,
                        self.legend_position,
                        self.legend_title,
                    ],
                )

        self.update()

    def update(self):
        if not self.mapbox.zoom:
            return
        if self.data is None:
            return
        if len(self.data) == 0:
            # Empty GeoDataFrame
            return            
        if self.mapbox.zoom > self.min_zoom and self.big_data and self.visible:
            coords = self.mapbox.map_extent
            xl0 = coords[0][0]
            xl1 = coords[1][0]
            yl0 = coords[0][1]
            yl1 = coords[1][1]
            
            # Limits WGS 84
            gdf = self.data.cx[xl0:xl1, yl0:yl1]
            
            self.unit = getattr(self, 'unit', '')
            if len(self.color_by_attribute) == 0:
                # Add new layer
                self.mapbox.runjs(
                    "./js/circle_layer.js",
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
                        self.unit                        
                    ],
                )
            elif len(self.color_by_attribute) > 0:
                # Color by attribute
                self.mapbox.runjs(
                    "./js/circle_layer_custom.js",
                    "addLayer",
                    arglist=[
                        self.map_id,
                        self.data,
                        self.hover_property,
                        self.unit,
                        self.min_zoom,
                        self.color_by_attribute,
                        self.legend_items,
                        self.legend_position,
                        self.legend_title,
                    ],
                )

    def activate(self):
        self.show()
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
        
        #Not working for color_by_attribute, so fixed with self.update()
        #TODO: make pretty
        self.update()

    def deactivate(self):
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
            self.set_visibility(False)
