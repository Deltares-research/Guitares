# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
import geopandas as gpd

from guitares.gui import GUI
from guitares.gui import find_element_by_id

class MapBoxExample:
    def __init__(self):

        self.main_path = os.path.dirname(os.path.abspath(__file__))
        self.server_path = os.path.join(self.main_path, "server")

        self.gui = GUI(self,
                       framework="pyqt5",
                       config_file="mapbox_example.yml",
                       config_path=self.main_path,
                       server_path=self.server_path,
                       server_port=3000,
                       stylesheet="Combinear.qss",
                       copy_mapbox_server_folder=True)

        # Define variables
        self.polygons  = gpd.GeoDataFrame()
        self.polylines = gpd.GeoDataFrame()
        self.markers   = gpd.GeoDataFrame()

        # Define GUI variables
        self.gui.setvar("mpbox", "polygon_names", [])
        self.gui.setvar("mpbox", "polygon_index", 0)
        self.gui.setvar("mpbox", "nr_polygons", 0)
        self.gui.setvar("mpbox", "polyline_names", [])
        self.gui.setvar("mpbox", "polyline_index", 0)
        self.gui.setvar("mpbox", "nr_polylines", 0)


    def on_build(self):
        # Executed after the GUI has been built up (optional)
        pass

    def on_map_ready(self):
        # Executed after the MapBox map has been loaded

        # Find the map widget
        element = find_element_by_id(self.gui.config["element"], "map")
        self.map = element["widget"]

        # Add container layer to the map
        layer = self.map.add_layer("main")

        # Add the draw layers
        from draw import add_draw_layers
        add_draw_layers()

        # Add the marker layer
        from markers import add_marker_layer
        add_marker_layer()

        # Set map view to 55 Columbia Ave in Cranston, RI
        self.map.fly_to(-71.39322, 41.77692, 13)


mpbox = MapBoxExample()
