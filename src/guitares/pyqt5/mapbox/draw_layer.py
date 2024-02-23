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
    def __init__(
        self,
        mapbox,
        id,
        map_id,
        shape="polygon",
        create=None,
        modify=None,
        select=None,
        deselect=None,
        add=None,
        rotate=True,
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
        circle_radius=4,
    ):
        super().__init__(mapbox, id, map_id)

        self.active = False
        self.type = "draw"
        self.shape = shape
        self.mode = (
            "active"  # Draw layers can have three modes: active, inactive, invisible
        )
        self.gdf = gpd.GeoDataFrame()
        self.create   = create
        self.modify   = modify
        self.select   = select
        self.deselect = deselect
        self.add      = add

        # Get Hex values for colors
        self.paint_props = {}
        self.paint_props["polygon_line_color"] = mcolors.to_hex(polygon_line_color)
        self.paint_props["polygon_line_width"] = polygon_line_width
        self.paint_props["polygon_line_style"] = polygon_line_style
        self.paint_props["polygon_line_opacity"] = polygon_line_opacity
        self.paint_props["polygon_fill_color"] = mcolors.to_hex(polygon_fill_color)
        self.paint_props["polygon_fill_opacity"] = polygon_fill_opacity
        self.paint_props["polyline_line_color"] = mcolors.to_hex(polyline_line_color)
        self.paint_props["polyline_line_width"] = polyline_line_width
        self.paint_props["polyline_line_style"] = polyline_line_style
        self.paint_props["polyline_line_opacity"] = polyline_line_opacity
        self.paint_props["circle_line_color"] = mcolors.to_hex(circle_line_color)
        self.paint_props["circle_line_opacity"] = circle_line_opacity
        self.paint_props["circle_fill_color"] = mcolors.to_hex(circle_fill_color)
        self.paint_props["circle_fill_opacity"] = circle_fill_opacity
        self.paint_props["circle_radius"] = circle_radius
        self.paint_props["rotate"] = rotate

        # Add this layer
        self.mapbox.runjs(
            "./js/draw_layer.js",
            "addLayer",
            arglist=[self.map_id, "active", self.paint_props, self.shape],
        )

    def set_mode(self, mode):
        """Set mode of layer. Can be active, inactive or invisible."""
        self.mode = mode
        if mode == "active":
            self.active = True
            self.visible = True
        elif mode == "inactive":
            self.active = False
            self.visible = True
        else:
            self.active = False
            self.visible = False
        self.mapbox.runjs("./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, mode])

    def activate(self):
        """Activate the draw layer so it can be edited by the user."""
        self.active = True
        self.mapbox.runjs("./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "active"])

    def deactivate(self):
        """Deactivate the draw layer so it can not be edited by the user."""
        self.active = False
        self.mapbox.runjs("./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "inactive"])

    # def show(self):
    #     self.visible = True
    #     if self.active:
    #         self.mapbox.runjs("./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "active"])
    #     else:
    #         self.mapbox.runjs("./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "inactive"])    

    # def hide(self):
    #     self.visible = False
    #     self.mapbox.runjs("./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "invisible"])

    # def set_mode(self, mode):
    #     self.mode = mode
    #     self.mapbox.runjs("./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, mode])

    def set_visibility(self, true_or_false):
        if true_or_false:
            if self.active:
                self.mapbox.runjs("./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "active"])
            else:
                self.mapbox.runjs("./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "inactive"])    
        else:
            # Make layer invisible
            self.mapbox.runjs("./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "invisible"])    

    def set_data(self, gdf):
        """Clear the draw layer and add data. Data must be a GeoDataFrame."""
        self.clear()
        self.add_feature(gdf)

    def add_feature(self, gdf):
        """Add data to draw layer. Data must be a GeoDataFrame."""
        # Loop through features
        if len(gdf) == 0:
            return
    
        # Append to self.gdf (which doesn't have to have CRS=4326)
        if not self.gdf.empty:
            self.gdf = self.gdf.append(gdf.to_crs(self.gdf.crs), ignore_index=True)
        else:
            self.gdf = gdf
        
        for index, row in gdf.to_crs(4326).iterrows():
            # Add feature to draw layer, which has CRS=4326
            gdf = gpd.GeoDataFrame(geometry=[row["geometry"]], crs=4326)
            self.mapbox.runjs("./js/draw_layer.js", "addFeature", arglist=[gdf, self.map_id])

    def add_rectangle(self, x0, y0, lenx, leny, rotation):
        """Add rectangle to draw layer."""
        x = [x0]
        y = [y0]
        x.append(x[0] + lenx * math.cos(math.pi*rotation/180))
        y.append(y[0] + lenx * math.sin(math.pi*rotation/180))
        x.append(x[1] + leny * math.cos(math.pi*(rotation + 90.0)/180))
        y.append(y[1] + leny * math.sin(math.pi*(rotation + 90.0)/180))
        x.append(x[2] + lenx * math.cos(math.pi*(rotation + 180.0)/180))
        y.append(y[2] + lenx * math.sin(math.pi*(rotation + 180.0)/180))
        x.append(x0)
        y.append(y0)
        polygon_crs = Polygon(zip(x, y))
        # Transform to WGS 84
        project = pyproj.Transformer.from_crs(
            self.mapbox.crs, pyproj.CRS(4326), always_xy=True
        ).transform
        polygon_wgs84 = transform(project, polygon_crs)
        gdf = gpd.GeoDataFrame(geometry=[polygon_wgs84], crs=4326)
        self._x0 = x0
        self._y0 = y0
        self._dx = lenx
        self._dy = leny
        self._rotation = math.pi*rotation/180
        self.add_feature(gdf)

    def draw(self):
        """Activate drawing mode."""
        if self.shape == "polygon":
            self.mapbox.runjs("./js/draw_layer.js", "drawPolygon", arglist=[self.map_id])
        elif self.shape == "polyline":
            self.mapbox.runjs("./js/draw_layer.js", "drawPolyline", arglist=[self.map_id])
        elif self.shape == "rectangle":
            self.mapbox.runjs("./js/draw_layer.js", "drawRectangle", arglist=[self.map_id])

    def set_gdf(self, feature_collection, compute_geometry=True):
        # Called after a feature has been drawn or added. A new GeoDataFrame is created for this layer.
        for feature in feature_collection["features"]:
            feature["properties"]["id"] = feature["id"]
        gdf = gpd.GeoDataFrame.from_features(feature_collection, crs=4326).to_crs(
            self.mapbox.crs
        )
        if self.shape == "rectangle":
            if compute_geometry:
                x0, y0, dx, dy, rotation = get_rectangle_geometry(gdf["geometry"])
                # Add columns with geometry info
                gdf["x0"] = x0
                gdf["y0"] = y0
                gdf["dx"] = dx
                gdf["dy"] = dy
                gdf["rotation"] = rotation
            else:
                gdf["x0"] = self._x0
                gdf["y0"] = self._y0
                gdf["dx"] = self._dx
                gdf["dy"] = self._dy
                gdf["rotation"] = self._rotation
        self.gdf = gdf

    def get_feature_index(self, feature_id):
        """Get a features index by ID in the GeoDataFrame."""
        feature_index = None
        if len(self.gdf) > 0:
            indx = self.gdf.index[self.gdf["id"] == feature_id].tolist()
            if indx:
                feature_index = indx[0]
        if feature_index is None:
            print("Could not find feature ...")
        return feature_index

    def get_feature_id(self, feature_index):
        """Get a features ID by index in the GeoDataFrame."""
        feature_id = None
        if len(self.gdf) > 0 and len(self.gdf) >= feature_index + 1:
            feature_id = self.gdf.loc[feature_index, "id"]
        return feature_id

    def feature_drawn(self, feature_collection, feature_id):
        # Called after a feature has been drawn by the user
        self.set_gdf(feature_collection)
        if self.create:
            feature_index = self.get_feature_index(feature_id)
            self.create(self.gdf, feature_index, feature_id)
        if self.shape == "rectangle" and not self.mapbox.crs.is_geographic:
            feature_index = self.get_feature_index(feature_id)
            x0 = self.gdf.loc[feature_index, "x0"]  
            y0 = self.gdf.loc[feature_index, "y0"]
            lenx = self.gdf.loc[feature_index, "dx"]
            leny = self.gdf.loc[feature_index, "dy"]
            rotation = self.gdf.loc[feature_index, "rotation"]*180/math.pi
            self.delete_feature(feature_id)
            self.add_rectangle(x0, y0, lenx, leny, rotation)

    def feature_added(self, feature_collection, feature_id):
        # Called after a feature has been added by the application
        self.set_gdf(feature_collection, compute_geometry=False)
#        self.set_visibility(True)
#        self.set_mode(self.mode)
        if self.add:
            feature_index = self.get_feature_index(feature_id)
            self.add(self.gdf, feature_index, feature_id)

    def feature_modified(self, feature_collection, feature_id):
        # Called after a feature has been modified by the user
        self.set_gdf(feature_collection)
        if self.modify:
            feature_index = self.get_feature_index(feature_id)
            self.modify(self.gdf, feature_index, feature_id)

    def feature_selected(self, feature_collection, feature_id):
        # Called after a feature has been selected by the user
        if self.select:
            feature_index = self.get_feature_index(feature_id)
            self.select(feature_index)

    def feature_deselected(self):
        # Called after a feature has been de-selected by the user
        if self.deselect:
            self.deselect()

    def activate_feature(self, feature_id_or_index):
        """Activate a feature by ID or index so it can be edited by the user."""
        if isinstance(feature_id_or_index, int):
            # It's an index
            index = feature_id_or_index
            feature_id = self.get_feature_id(index)
        else:
            feature_id = feature_id_or_index    
        if self.mode != "active":
            self.mode = "active"
            self.mapbox.runjs(
                "./js/draw_layer.js", "setLayerMode", arglist=[self.map_id, self.mode]
            )
        self.mapbox.runjs("./js/draw_layer.js", "activateFeature", arglist=[feature_id])

    def set_feature_geometry(self, feature_id, geom):        
        self.mapbox.runjs("./js/draw_layer.js", "setFeatureGeometry", arglist=[self.map_id, feature_id, geom])

    def delete_feature(self, feature_id_or_index):
        """Delete a feature by ID or index"""
        if isinstance(feature_id_or_index, int):
            # It's an index
            index = feature_id_or_index
            feature_id = self.get_feature_id(index)
            # Remove from gdf
            self.gdf = self.gdf.drop(index)
            if len(self.gdf) > 0:
                self.gdf = self.gdf.reset_index(drop=True)
            else:
                self.gdf = gpd.GeoDataFrame()
            # Remove from map
            self.mapbox.runjs("./js/draw_layer.js", "deleteFeature", arglist=[feature_id])
        else:    
            feature_id = feature_id_or_index
            # Remove from gdf
            for index, row in self.gdf.iterrows():
                if row["id"] == feature_id:
                    self.gdf = self.gdf.drop(index)
                    if len(self.gdf) > 0:
                        self.gdf = self.gdf.reset_index(drop=True)
                    else:
                        self.gdf = gpd.GeoDataFrame()    
                    break
            self.mapbox.runjs("./js/draw_layer.js", "deleteFeature", arglist=[feature_id])
        return self.gdf    

    def delete_from_map(self):
        """Delete the draw layer from the map."""
        self.active = False
        self.mapbox.runjs("./js/draw_layer.js", "deleteLayer", arglist=[self.map_id])
        self.gdf = gpd.GeoDataFrame()

    def clear(self):
        """Clear the draw layer."""
        for index, row in self.gdf.iterrows():
            self.mapbox.runjs("./js/draw_layer.js", "deleteFeature", arglist=[row["id"]])
        self.gdf = gpd.GeoDataFrame()

    def get_gdf(self, id=None):
        """Return the GeoDataFrame for this layer. If id is specified, return only the row with that id."""
        if id:
            for index, row in self.gdf.iterrows():
                if row["id"] == id:
                    return self.gdf[index]
        else:
            return self.gdf

    def redraw(self):
        # Add this layer
        self.mapbox.runjs(
            "./js/draw_layer.js",
            "addLayer",
            arglist=[self.map_id, "active", self.paint_props, self.shape],
        )
        self.add_feature(self.gdf)
        self.set_mode(self.mode)
        if not self.get_visibility():
            self.set_visibility(False)

def get_rectangle_geometry(geoms):
    x0 = []
    y0 = []
    dx = []
    dy = []
    rotation = []
    for geom in geoms:
        xx, yy = geom.exterior.coords.xy
        x0.append(float(xx[0]))
        y0.append(float(yy[0]))
        lenx = math.sqrt(float(xx[1] - xx[0])**2 + float(yy[1] - yy[0])**2)
        leny = math.sqrt(float(xx[2] - xx[1])**2 + float(yy[2] - yy[1])**2)
        dx.append(lenx)
        dy.append(leny)
        rot = float((math.atan2(yy[1] - yy[0], xx[1] - xx[0])))
        if abs(rot*180/math.pi) < 1.0:
            rot = 0.0
        rotation.append(rot)

    return x0, y0, dx, dy, rotation
