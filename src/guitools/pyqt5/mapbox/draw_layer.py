import geopandas as gpd
import pandas as pd
import json
import geojson
import shapely
from PyQt5 import QtCore

from .layer import Layer, list_layers

class DrawLayer(Layer):
    def __init__(self, mapbox, id, map_id, create=None, modify=None, select=None):
        super().__init__(mapbox, id, map_id)
        self.active = False
        self.type   = "draw"
        self.gdf    = gpd.GeoDataFrame()
        self.create_callback = create
        self.modify_callback = modify
        self.select_callback = select

    def activate(self):

        # De-activate all other draw layers
        draw_layers = list_layers(self.mapbox.layer, layer_type="draw")
        for layer in draw_layers:
            # Only de-activate other layers that are currently active
            if layer.active and layer.map_id is not self.map_id:
                layer.deactivate()

        # And activate the current draw layer
        if not self.active:
            self.active = True
            # First clear existing features in mapbox draw layer

            # And now add drawing features
            for index, row in self.gdf.iterrows():
                geom = row["geometry"]
                feature_id = row["id"]
                # Remove feature from draw layer
                js_string = "import('./js/draw.js').then(module => {module.deleteInactiveFeature('" + feature_id + "')});"
                self.mapbox.view.page().runJavaScript(js_string)
                # Add feature as geojson layer
                gjsn = geojson.Polygon(geom.exterior.coords)
                gjsn["coordinates"] = [gjsn["coordinates"]]
                js_string = "import('./js/draw.js').then(module => {module.addActiveFeature('" + feature_id + "'," + json.dumps(gjsn) + ")});"
                self.mapbox.view.page().runJavaScript(js_string)


    def deactivate(self):
        self.active = False
        # Loop through draw features
        for index, row in self.gdf.iterrows():
            geom = row["geometry"]
            feature_id = row["id"]
            # Remove feature from draw layer
            js_string = "import('./js/draw.js').then(module => {module.deleteActiveFeature('" + feature_id + "')});"
            self.mapbox.view.page().runJavaScript(js_string)
            # Add feature as geojson layer
            gjsn = geojson.Polygon(geom.exterior.coords)
            gjsn["coordinates"] = [gjsn["coordinates"]]
            js_string = "import('./js/draw.js').then(module => {module.addInactiveFeature('" + feature_id + "'," + json.dumps(gjsn) + ")});"
            self.mapbox.view.page().runJavaScript(js_string)

    def add_feature(self, feature_id, geometry):
        self.active = False
        # Loop through draw features
        fstring = json.dumps(geometry)
        js_string = "import('./js/draw.js').then(module => {module.addInactiveFeature('" + feature_id + "'," + fstring + ")});"
        self.mapbox.view.page().runJavaScript(js_string)
        #
        # for index, row in self.gdf.iterrows():
        #     geom = row["geometry"]
        #     feature_id = row["id"]
        #     # Remove feature from draw layer
        #     js_string = "import('/draw.js').then(module => {module.deleteActiveFeature('" + feature_id + "')});"
        #     self.mapbox.view.page().runJavaScript(js_string)
        #     # Add feature as geojson layer
        #     gjsn = geojson.Polygon(geom.exterior.coords)
        #     gjsn["coordinates"] = [gjsn["coordinates"]]
        #     js_string = "import('/draw.js').then(module => {module.addInactiveFeature('" + feature_id + "'," + json.dumps(gjsn) + ")});"
        #     self.mapbox.view.page().runJavaScript(js_string)

    def draw_polygon(self):
        # Activate this draw layer (all the other draw layers are automatically de-activated)
        self.mapbox.active_draw_layer = self
        self.activate()
        js_string = "import('./js/draw.js').then(module => {module.drawPolygon('" + self.map_id + "')});"
        self.mapbox.view.page().runJavaScript(js_string)

    def feature_drawn(self, coords, feature_id, feature_type):
        if feature_type == "polygon":
            geom = shapely.geometry.Polygon(coords[0])
        gdf = gpd.GeoDataFrame(data=[feature_id], columns=["id"], crs='epsg:4326', geometry=[geom])
        self.gdf = pd.concat([self.gdf, gdf])
        if self.create_callback:
            self.create_callback(gdf)

    def feature_modified(self, coords, feature_id, feature_type):
        if feature_type == "polygon":
            geom = shapely.geometry.Polygon(coords[0])
        gdf = gpd.GeoDataFrame(data=[feature_id], columns=["id"], crs='epsg:4326', geometry=[geom])
        for index, row in self.gdf.iterrows():
            feature_id = row["id"]
            if row["id"] == feature_id:
                row["geometry"] = geom
                break
        if self.modify_callback:
            self.modify_callback(gdf)

    def feature_selected(self, feature_id):
        if self.select_callback:
            self.select_callback(feature_id)

    def activate_feature(self, feature_id):
        js_string = "import('./js/draw.js').then(module => {module.activateFeature('" + feature_id + "')});"
        self.mapbox.view.page().runJavaScript(js_string)

    def delete_feature(self, feature_id):
        js_string = "import('./js/draw.js').then(module => {module.deleteActiveFeature('" + feature_id + "')});"
        self.mapbox.view.page().runJavaScript(js_string)

    def clear(self):
        self.active = False
        # Loop through draw features
        for index, row in self.gdf.iterrows():
            feature_id = row["id"]
            # Remove feature from draw layer
            js_string = "import('./js/draw.js').then(module => {module.deleteActiveFeature('" + feature_id + "')});"
            self.mapbox.view.page().runJavaScript(js_string)
            js_string = "import('./js/draw.js').then(module => {module.deleteInactiveFeature('" + feature_id + "')});"
            self.mapbox.view.page().runJavaScript(js_string)

#     @QtCore.pyqtSlot(str, str, str)
#     def polygonDrawn(self, coord_string, feature_id, layer_id):
# #        self.active_layer.create_feature(json.loads(coord_string), feature_id, "polygon")
#         coords = json.loads(coord_string)
#         geometry = shapely.geometry.Polygon(coords[0])
#         gdf = gpd.GeoDataFrame(data=[feature_id], columns=["id"], crs='epsg:4326', geometry=[geometry])
#         self.gdf = pd.concat([self.gdf, gdf])
#         if self.create_callback:
#             self.create_callback(gdf)


    # def draw_polyline(self, layer_name, create=None, modify=None):
    #     layer_group_name = "_base"
    #     js_string = "import('/main.js').then(module => {module.drawPolyline('" + layer_group_name + "','" + layer_name + "');});"
    #     self.view.page().runJavaScript(js_string)
    #     self.polyline_create_callback = None
    #     self.polyline_modify_callback = None
    #     if create:
    #         self.polyline_create_callback = create
    #     if modify:
    #         self.polyline_modify_callback = modify
    #
    # def draw_point(self, layer_group_name, layer_name):
    #     js_string = "import('/main.js').then(module => {module.drawPoint('" + layer_group_name + "','" + layer_name + "');});"
    #     self.view.page().runJavaScript(js_string)
    #
    # def draw_rectangle(self, layer_name, create=None, modify=None):
    #     layer_group_name = "_base"
    #     js_string = "import('/main.js').then(module => {module.drawRectangle('" + layer_group_name + "','" + layer_name + "');});"
    #     self.view.page().runJavaScript(js_string)
    #     self.rectangle_create_callback = None
    #     self.rectangle_modify_callback = None
    #     if create:
    #         self.rectangle_create_callback = create
    #     if modify:
    #         self.rectangle_modify_callback = modify
