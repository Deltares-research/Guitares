import math
import geopandas as gpd
import matplotlib.colors as mcolors
import shapely
import json
from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj

from .layer import Layer

class DrawLayer(Layer):
    def __init__(self, mapbox, id, map_id,
                 shape="polygon",
                 create=None,
                 modify=None,
                 select=None,
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
        self.shape  = shape
        self.mode   = "active" # Draw layers can have three modes: active, inactive, invisible
        self.gdf    = gpd.GeoDataFrame()
        self.create = create
        self.modify = modify
        self.select = select

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

    def add_rectangle(self, feature_id, x0, y0, lenx, leny, rotation):
        shape = "rectangle"
        lon_point_list = [x0, x0 + lenx, x0 + lenx, x0, x0]
        lat_point_list = [y0, y0, y0 + leny, y0 + leny, y0]
        polygon_crs = Polygon(zip(lon_point_list, lat_point_list))
        # Transform to WGS 84
        project = pyproj.Transformer.from_crs(self.crs, pyproj.CRS(4326), always_xy=True).transform
        polygon_wgs84 = transform(project, polygon_crs)
        json_string = shapely.to_geojson(polygon_wgs84)
        geometry = json.loads(json_string)
        self.add_feature(feature_id, shape, geometry)

    def draw(self):
        self.mapbox.active_draw_layer = self
        if self.shape == "polygon":
            self.mapbox.runjs("./js/draw.js", "drawPolygon", arglist=[self.map_id])
        elif self.shape == "polyline":
            self.mapbox.runjs("./js/draw.js", "drawPolyline", arglist=[self.map_id])
        elif self.shape == "rectangle":
            self.mapbox.runjs("./js/draw.js", "drawRectangle", arglist=[self.map_id])

    def feature_drawn(self, feature_collection, feature_id):
        for feature in feature_collection["features"]:
            feature["properties"]["id"] = feature["id"]
        gdf = gpd.GeoDataFrame.from_features(feature_collection, crs=4326).to_crs(self.crs)
        feature_index = None
        if len(gdf)>0:
            indx = gdf.index[gdf["id"]==feature_id].tolist()
            if indx:
                feature_index = indx[0]
        if feature_index is None:
            print("Could not find feature ...")
            return
        if self.shape == "rectangle":
            x0, y0, dx, dy, rotation = get_rectangle_geometry(gdf["geometry"])
            # Add columns with geometry info
            gdf["x0"] = x0
            gdf["y0"] = y0
            gdf["dx"] = dx
            gdf["dy"]= dy
            gdf["rotation"] = rotation
        self.gdf = gdf    
        if self.create:
            self.create(gdf, feature_index, feature_id)

    def feature_modified(self, feature_collection, feature_id):
        for feature in feature_collection["features"]:
            feature["properties"]["id"] = feature["id"]
        gdf = gpd.GeoDataFrame.from_features(feature_collection, crs=4326).to_crs(self.crs)
        feature_index = None
        if len(gdf)>0:
            indx = gdf.index[gdf["id"]==feature_id].tolist()
            if indx:
                feature_index = indx[0]
        if feature_index is None:
            print("Could not find feature ...")
            return
        if self.shape == "rectangle":
            x0, y0, dx, dy, rotation = get_rectangle_geometry(gdf["geometry"])
            # Add columns with geometry info
            gdf["x0"] = x0
            gdf["y0"] = y0
            gdf["dx"] = dx
            gdf["dy"]= dy
            gdf["rotation"] = rotation
        self.gdf = gdf    
        if self.modify:
            self.modify(gdf, feature_index, feature_id)

    def feature_selected(self, feature_collection, feature_id):
        for feature in feature_collection["features"]:
            feature["properties"]["id"] = feature["id"]
        gdf = gpd.GeoDataFrame.from_features(feature_collection, crs=4326).to_crs(self.crs)
        feature_index = None
        if len(gdf)>0:
            indx = gdf.index[gdf["id"]==feature_id].tolist()
            if indx:
                feature_index = indx[0]
        if feature_index is None:
            print("Could not find feature ...")
            return
        if self.select:
            self.select(feature_index)

    def activate_feature(self, feature_id):
        if self.mode != "active":
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
        # Loop through draw features
        for index, row in self.gdf.iterrows():
            feature_id = row["id"]
            # Remove feature from draw layer
            self.mapbox.runjs("./js/draw.js", "deleteFeature", arglist=[feature_id])
        # Empty GeoDataFrame
        self.gdf    = gpd.GeoDataFrame()

    def get_gdf(self, id=None):
        if id:
            for index, row in self.gdf.iterrows():
                if row["id"] == id:
                    return self.gdf[index]
        else:
            return self.gdf

def get_rectangle_geometry(geoms):
    x0 = []
    y0 = []
    dx = []
    dy = []
    rotation = []
    for geom in geoms:
        xx, yy = geom.exterior.coords.xy
        x0.append(xx[0])
        y0.append(yy[0])
        dx.append(xx[1] - xx[0])
        dy.append(yy[2] - yy[1])
        rotation.append(math.atan2(yy[1] - yy[0], xx[1] - xx[0]))
    return x0, y0, dx, dy, rotation
