# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
import geopandas as gpd
from shapely.geometry import Point

from guitares.gui import GUI

class MaplibreExample:
    def __init__(self):

        self.main_path = os.path.dirname(os.path.abspath(__file__))
        self.server_path = os.path.join(self.main_path, "server")

        self.gui = GUI(self,
                       framework="pyside6",
                       map_engine="maplibre",
                       config_file="maplibre_example.yml",
                       config_path=self.main_path,                  # path to the yml config files
                       server_path=self.server_path,                # path to the server
                       stylesheet="Combinear.qss")
        
        # Get map styles and copy to gui variables
        self.gui.setvar("example", "map_style_names", self.gui.map_styles)
        self.gui.setvar("example", "map_style_styles", self.gui.map_styles)
        self.gui.setvar("example", "map_style", self.gui.map_styles[0])

    def initialize(self):

        # Add a container layer
        layer = app.map.add_layer("container_layer")

        # Add a marker layer to the container layer
        layer.add_layer("marker_layer",
                          type="marker",
                          hover_property="description",
                          icon_file="mapbox-marker-icon-20px-orange.png",
                        #   click_property="url",
                          icon_size=1.0,
                        #   click_popup_width=600,
                        #   click_popup_height=220,
                         )
        # Create geodataframe with two points, crs(4326)
        gdf = gpd.GeoDataFrame(geometry=[Point(0.0, 0.0), Point(10.0, 0.0)], crs=4326)
        gdf["description"] = ["This is a marker at (0,0)", "This is a marker at (10,0)"]
        layer.layer["marker_layer"].set_data(gdf) 

        app.gui.window.update()


app = MaplibreExample()
