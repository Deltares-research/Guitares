import math
import geopandas as gpd
import pandas as pd
import json
import geojson
import shapely
import matplotlib.colors as mcolors

from .layer import Layer, list_layers
#from .mapbox import JavascriptString


class DrawLayer(Layer):
    def __init__(self, mapbox, id, map_id, create=None, modify=None, select=None,
                 polygon_line_color="dodgerblue",
                 polygon_line_width=2,
                 polygon_line_style="-",
                 polygon_line_opacity=1.0,
                 polygon_fill_color="dodgerblue",
                 polygon_fill_opacity=0.5,
                 polyline_line_color="limegreen",
                 polyline_line_width=2,
                 polyline_line_style="-",
                 polyline_line_opacity=1.0,
                 circle_line_color="black",
                 circle_line_opacity=1.0,
                 circle_fill_color="orangered",
                 circle_fill_opacity=0.5,
                 circle_radius=4):

        super().__init__(mapbox, id, map_id)

        self.active = False
        self.type   = "draw"
        self.mode   = "active" # Draw layers can have three modes: active, inactive, invisible
        self.gdf    = gpd.GeoDataFrame()
        self.create_callback = create
        self.modify_callback = modify
        self.select_callback = select

        # Get Hex values for colors
        self.paint_props = {}
        self.paint_props["polygon_line_color"]    = mcolors.to_hex(polygon_line_color)
        self.paint_props["polygon_line_width"]    = polygon_line_width
        self.paint_props["polygon_line_style"]    = polygon_line_style
        self.paint_props["polygon_line_opacity"]  = polygon_line_opacity
        self.paint_props["polygon_fill_color"]    = mcolors.to_hex(polygon_fill_color)
        self.paint_props["polygon_fill_opacity"]  = polygon_fill_opacity
        self.paint_props["polyline_line_color"]   = mcolors.to_hex(polyline_line_color)
        self.paint_props["polyline_line_width"]   = polyline_line_width
        self.paint_props["polyline_line_style"]   = polyline_line_style
        self.paint_props["polyline_line_opacity"] = polyline_line_opacity
        self.paint_props["circle_line_color"]     = mcolors.to_hex(circle_line_color)
        self.paint_props["circle_line_opacity"]   = circle_line_opacity
        self.paint_props["circle_fill_color"]     = mcolors.to_hex(circle_fill_color)
        self.paint_props["circle_fill_opacity"]   = circle_fill_opacity
        self.paint_props["circle_radius"]         = circle_radius

        # Add this layer
        self.mapbox.runjs("./js/draw.js", "addLayer", arglist=[self.map_id, "invisible", self.paint_props])

    def set_mode(self, mode):
        self.mode = mode
        self.mapbox.runjs("./js/draw.js", "setLayerMode", arglist=[self.map_id, mode])

    def set_visibility(self, true_or_false):
        if true_or_false:
            if self.mode == "invisible":
                # Make layer inactive
                self.set_mode("inactive")
        else:
            # Make layer invisible
            self.set_mode("invisible")

    def add_feature(self, feature_id, shape, geometry):
        self.mapbox.runjs("./js/draw.js", "addFeature", arglist=[feature_id, shape, geometry, self.map_id])

    def draw_polygon(self):
        self.mapbox.active_draw_layer = self
        self.mapbox.runjs("./js/draw.js", "drawPolygon", arglist=[self.map_id])

    def draw_polyline(self):
        self.mapbox.active_draw_layer = self
        self.mapbox.runjs("./js/draw.js", "drawPolyline", arglist=[self.map_id])

    def draw_rectangle(self):
        self.mapbox.active_draw_layer = self
        self.mapbox.runjs("./js/draw.js", "drawRectangle", arglist=[self.map_id])

    def feature_drawn(self, coords, feature_id, feature_shape):
        if feature_shape== "polygon":
            geom = shapely.geometry.Polygon(coords[0])
            gdf = gpd.GeoDataFrame(data=[[feature_id, feature_shape]], columns=["id", "shape"], crs='epsg:4326', geometry=[geom])
        if feature_shape == "polyline":
            geom = shapely.geometry.LineString(coords)
            gdf = gpd.GeoDataFrame(data=[[feature_id, feature_shape]], columns=["id", "shape"], crs='epsg:4326', geometry=[geom])
        if feature_shape == "rectangle":
            geom = shapely.geometry.Polygon(coords[0])
            x0, y0, dx, dy, rotation = get_rectangle_geometry(geom)
            gdf = gpd.GeoDataFrame(data=[[feature_id, feature_shape, x0, y0, dx, dy, rotation]], columns=["id", "shape", "x0", "y0", "dx", "dy", "rotation"], crs='epsg:4326', geometry=[geom])
        self.gdf = pd.concat([self.gdf, gdf], ignore_index=True)
        if self.create_callback:
            self.create_callback(gdf, feature_shape, feature_id)

    def feature_modified(self, coords, feature_id, feature_shape):
        if feature_shape == "polygon":
            geom = shapely.geometry.Polygon(coords[0])
            gdf = gpd.GeoDataFrame(data=[[feature_id, feature_shape]], columns=["id", "shape"], crs='epsg:4326', geometry=[geom])
        if feature_shape == "polyline":
            geom = shapely.geometry.LineString(coords)
            gdf = gpd.GeoDataFrame(data=[[feature_id, feature_shape]], columns=["id", "shape"], crs='epsg:4326', geometry=[geom])
        if feature_shape == "rectangle":
            geom = shapely.geometry.Polygon(coords[0])
            x0, y0, dx, dy, rotation = get_rectangle_geometry(geom)
            gdf = gpd.GeoDataFrame(data=[[feature_id, feature_shape, x0, y0, dx, dy, rotation]], columns=["id", "shape", "x0", "y0", "dx", "dy", "rotation"], crs='epsg:4326', geometry=[geom])
        for index, row in self.gdf.iterrows():
            if row["id"] == feature_id:
                self.gdf.at[index, "geometry"] = geom
                break
        if self.modify_callback:
            self.modify_callback(gdf, feature_shape, feature_id)

    def feature_selected(self, feature_id):
        if self.select_callback:
            self.select_callback(feature_id)

    def activate_feature(self, feature_id):
        if self.mode is not "active":
            self.mode = "active"
            self.mapbox.runjs("./js/draw.js", "setLayerMode", arglist=[self.map_id, mode])
        self.mapbox.runjs("./js/draw.js", "activateFeature", arglist=[feature_id])

    def delete_feature(self, feature_id):
        if feature_id: # Could also be None
            # Remove from gdf
            for index, row in self.gdf.iterrows():
                if row["id"] == feature_id:
                    self.gdf = self.gdf.drop(index)
                    break
            self.mapbox.runjs("./js/draw.js", "deleteFeature", arglist=[feature_id])

    def clear(self):
        self.active = False
        # Empty GeoDataFrame
        self.gdf    = gpd.GeoDataFrame()
        # Loop through draw features
        for index, row in self.gdf.iterrows():
            feature_id = row["id"]
            # Remove feature from draw layer
            self.mapbox.runjs("./js/draw.js", "deleteFeature", arglist=[feature_id])

    def get_gdf(self, id=None):
        if id:
            for index, row in self.gdf.iterrows():
                if row["id"] == id:
                    return self.gdf[index]
        else:
            return self.gdf

def get_rectangle_geometry(geom):
    xx, yy = geom.exterior.coords.xy
    x0 = xx[0]
    y0 = yy[0]
    dx = xx[1] - xx[0]
    dy = yy[2] - yy[1]
    rotation = math.atan2(yy[1] - yy[0], xx[1] - xx[0])
    return x0, y0, dx, dy, rotation
