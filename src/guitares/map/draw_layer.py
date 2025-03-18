import math
import pandas as pd
import geopandas as gpd
import matplotlib.colors as mcolors
import shapely
from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj

from .layer import Layer


class DrawLayer(Layer):
    def __init__(
        self,
        map,
        layer_id,
        map_id,
        columns={},
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
        super().__init__(map, layer_id, map_id)

        self.active = False
        self.type = "draw"
        self.shape = shape
        self.mode = (
            "active"  # Draw layers can have three modes: active, inactive, invisible
        )
        self.gdf = gpd.GeoDataFrame()
        self.columns = columns
        self.create = create
        self.modify = modify
        self.select = select
        self.deselect = deselect
        self.add = add

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
        self.map.runjs(
            "/js/draw_layer.js",
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
        self.map.runjs("/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, mode])

    def activate(self):
        """Activate the draw layer so it can be edited by the user."""
        self.visible = True
        self.active = True
        self.map.runjs(
            "/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "active"]
        )

    def deactivate(self):
        """Deactivate the draw layer so it can not be edited by the user."""
        self.active = False
        self.map.runjs(
            "/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "inactive"]
        )

    # def show(self):
    #     self.visible = True
    #     if self.active:
    #         self.map.runjs("/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "active"])
    #     else:
    #         self.map.runjs("/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "inactive"])

    # def hide(self):
    #     self.visible = False
    #     self.map.runjs("/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "invisible"])

    # def set_mode(self, mode):
    #     self.mode = mode
    #     self.map.runjs("/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, mode])

    def set_visibility(self, true_or_false):
        if true_or_false:
            if self.active:
                self.map.runjs(
                    "/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "active"]
                )
            else:
                self.map.runjs(
                    "/js/draw_layer.js",
                    "setLayerMode",
                    arglist=[self.map_id, "inactive"],
                )
        else:
            # Make layer invisible
            self.map.runjs(
                "/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "invisible"]
            )

    def set_data(self, gdf):
        """Clear the draw layer and add data. Data must be a GeoDataFrame."""
        self.clear()
        self.add_feature(gdf)

    def add_feature(self, gdf):
        """Add data to draw layer. Data must be a GeoDataFrame."""

        if len(gdf) == 0:
            return

        # Append to self.gdf (which doesn't have to have CRS=4326)
        if not self.gdf.empty:
            self.gdf = pd.concat(
                [self.gdf, gdf.to_crs(self.gdf.crs)], ignore_index=True
            )
        else:
            self.gdf = gdf

        for index, row in gdf.to_crs(4326).iterrows():
            # Add feature to draw layer, which has CRS=4326
            gdf2plot = gpd.GeoDataFrame(geometry=[row["geometry"]])
            # if "name" in row:
            #     gdf["name"] = row["name"]
            self.map.runjs(
                "/js/draw_layer.js", "addFeature", arglist=[gdf2plot, self.map_id]
            )

    def add_rectangle(self, x0, y0, lenx, leny, rotation):
        """Add rectangle to draw layer."""
        x = [x0]
        y = [y0]
        x.append(x[0] + lenx * math.cos(math.pi * rotation / 180))
        y.append(y[0] + lenx * math.sin(math.pi * rotation / 180))
        x.append(x[1] + leny * math.cos(math.pi * (rotation + 90.0) / 180))
        y.append(y[1] + leny * math.sin(math.pi * (rotation + 90.0) / 180))
        x.append(x[2] + lenx * math.cos(math.pi * (rotation + 180.0) / 180))
        y.append(y[2] + lenx * math.sin(math.pi * (rotation + 180.0) / 180))
        x.append(x0)
        y.append(y0)
        polygon_crs = Polygon(zip(x, y))
        # Transform to WGS 84
        project = pyproj.Transformer.from_crs(
            self.map.crs, pyproj.CRS(4326), always_xy=True
        ).transform
        polygon_wgs84 = transform(project, polygon_crs)
        gdf = gpd.GeoDataFrame(geometry=[polygon_wgs84], crs=4326)
        gdf["x0"] = x0
        gdf["y0"] = y0
        gdf["dx"] = lenx
        gdf["dy"] = leny
        gdf["rotation"] = rotation
        self.add_feature(gdf)

    def draw(self):
        """Activate drawing mode."""
        if self.shape == "polygon":
            self.map.runjs("/js/draw_layer.js", "drawPolygon", arglist=[self.map_id])
        elif self.shape == "polyline":
            self.map.runjs("/js/draw_layer.js", "drawPolyline", arglist=[self.map_id])
        elif self.shape == "rectangle":
            self.map.runjs("/js/draw_layer.js", "drawRectangle", arglist=[self.map_id])

    def set_gdf(self, feature_collection, index):

        # Called after a feature has been drawn or added. A new GeoDataFrame is created for this layer.
        gdf = gpd.GeoDataFrame.from_features(feature_collection, crs=4326).to_crs(
            self.map.crs
        )

        feature_id = feature_collection["features"][index]["id"]

        if index > len(self.gdf) - 1:
            # Add new row to self.gdf
            d = {"geometry": [gdf.iloc[index]["geometry"]], "id": [feature_id]}
            if self.columns:
                for col in self.columns:
                    d[col] = [self.columns[col]]
            new_row = gpd.GeoDataFrame(d).set_crs(self.map.crs)
            # Add new row to self.gdf (this means that the dataframe will get a new memory address)
            self.gdf = pd.concat([self.gdf, new_row], ignore_index=True)
            pass
        else:
            # Only change the geometry of the selected feature and copy the id
            # self.gdf.at[index, "id"] = gdf.at[index, "id"]
            self.gdf.at[index, "id"] = feature_id
            self.gdf.at[index, "geometry"] = gdf.at[index, "geometry"]

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

        # Feature index is always the last in the feature collection
        feature_index = len(feature_collection["features"]) - 1

        # Called after a feature has been drawn by the user
        if self.shape == "rectangle":
            # Need to make sure that the rectangle is drawn in ccw direction
            # with the lower left corner as the first point
            geom = feature_collection["features"][feature_index]["geometry"]
            geom = fix_rectangle_geometry(geom)
            feature_collection["features"][feature_index]["geometry"] = geom

        # Create geodataframe from feature collection
        self.set_gdf(feature_collection, feature_index)

        # Check if this is a rectangle. If so, we need to compute the geometry and redraw it,
        # since the polygon may have been changed.
        if self.shape == "rectangle":
            # Now compute geometry for rectangle that was just drawn
            # Not geom is in the map CRS, not necessarily 4326
            geom = self.gdf.loc[feature_index, "geometry"]
            x0, y0, dx, dy, rotation = get_rectangle_geometry(geom)
            self.gdf.at[feature_index, "x0"] = x0
            self.gdf.at[feature_index, "y0"] = y0
            self.gdf.at[feature_index, "dx"] = dx
            self.gdf.at[feature_index, "dy"] = dy
            self.gdf.at[feature_index, "rotation"] = 0.0 # When drawing a rectangle, the rotation is always 0.0
            # Need to set the corrected rectangle geometry, but it has to be in 4326
            # Transform to WGS 84
            project = pyproj.Transformer.from_crs(
                self.map.crs, pyproj.CRS(4326), always_xy=True
            ).transform
            geom = transform(project, geom) 
            self.set_feature_geometry(feature_id, geom)

        # Check if there is a create method
        if self.create:
            # Call the create method sending the gdf with all features and the index of the new feature
            self.create(self.gdf, feature_index, feature_id)

    def feature_added(self, feature_collection, feature_id):
        # Called after a feature has been added by the application
        index = len(feature_collection["features"]) - 1
        self.set_gdf(feature_collection, index)
        if self.add:
            feature_index = self.get_feature_index(feature_id)
            self.add(self.gdf, feature_index, feature_id)

    def feature_modified(self, feature_collection, feature_id):
        # Called after a feature has been modified by the user
        index = self.get_feature_index(feature_id)
        self.set_gdf(feature_collection, index)

        if self.shape == "rectangle":
            # Need to set rectangle geometry
            geom = self.gdf.loc[index, "geometry"]
            x0, y0, dx, dy, rotation = get_rectangle_geometry(geom)
            self.gdf.at[index, "x0"] = x0
            self.gdf.at[index, "y0"] = y0
            self.gdf.at[index, "dx"] = dx
            self.gdf.at[index, "dy"] = dy
            self.gdf.at[index, "rotation"] = rotation

        if self.modify:
            self.modify(self.gdf, index, feature_id)

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
            self.map.runjs(
                "/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, self.mode]
            )
        self.map.runjs("/js/draw_layer.js", "activateFeature", arglist=[feature_id])

    def set_feature_geometry(self, feature_id, geom):
        # This does not work!
        if hasattr(geom, "__geo_interface__"):
            # Shapely geometry, turn into dict
            geom = geom.__geo_interface__
        self.map.runjs(
            "/js/draw_layer.js",
            "setFeatureGeometry",
            arglist=[self.map_id, feature_id, geom],
        )

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
            self.map.runjs("/js/draw_layer.js", "deleteFeature", arglist=[feature_id])
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
            self.map.runjs("/js/draw_layer.js", "deleteFeature", arglist=[feature_id])
        return self.gdf

    def delete_from_map(self):
        """Delete the draw layer from the map."""
        self.active = False
        self.map.runjs("/js/draw_layer.js", "deleteLayer", arglist=[self.map_id])
        self.gdf = gpd.GeoDataFrame()

    def clear(self):
        """Clear the draw layer."""
        for index, row in self.gdf.iterrows():
            self.map.runjs("/js/draw_layer.js", "deleteFeature", arglist=[row["id"]])
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
        self.map.runjs(
            "/js/draw_layer.js",
            "addLayer",
            arglist=[self.map_id, "active", self.paint_props, self.shape],
        )
        self.add_feature(self.gdf)
        self.set_mode(self.mode)
        if not self.get_visibility():
            self.set_visibility(False)


def get_rectangle_geometry(geom):
    xx, yy = geom.exterior.coords.xy
    x0 = float(xx[0])
    y0 = float(yy[0])
    dx = math.sqrt(float(xx[1] - xx[0]) ** 2 + float(yy[1] - yy[0]) ** 2)
    dy = math.sqrt(float(xx[2] - xx[1]) ** 2 + float(yy[2] - yy[1]) ** 2)
    rotation = float((math.atan2(yy[1] - yy[0], xx[1] - xx[0])))
    if abs(rotation * 180 / math.pi) < 1.0:
        rotation = 0.0
    return x0, y0, dx, dy, rotation


def fix_rectangle_geometry(geom):
    # This ensures that the rectangle is drawn CCW direction with the lower left corner as the first point (what a mess ...)
    # Check if the geometry is a polygon
    # Check if this ccw
    if not shapely.is_ccw(shapely.LineString(geom["coordinates"][0])):
        # Reverse the order of the coordinates
        geom["coordinates"][0] = geom["coordinates"][0][::-1]
    coords = geom["coordinates"][0]
    # Remove the last point which is the same as the first
    coords = coords[0:-1]
    # Get lower left corner by taking minimum x and y values
    min_x = min([x for x, y in coords])
    min_y = min([y for x, y in coords])
    # Now find the index of the point closest to the lower left corner
    dst = [(x - min_x) ** 2 + (y - min_y) ** 2 for x, y in coords]
    index = dst.index(min(dst))
    new_first_point = coords[
        index
    ]  # Assuming you want the third point as the new first point
    new_coords = [new_first_point] + coords[index + 1 :] + coords[0:index]
    new_coords.append(new_coords[0])
    # Create a new polygon with the updated coordinates
    new_polygon = Polygon(new_coords)
    # Update the geometry
    geom = new_polygon.__geo_interface__
    return geom
