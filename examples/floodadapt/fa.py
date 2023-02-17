# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
import geopandas as gpd

from guitares.gui import GUI
from guitares.gui import find_element_by_id

class FloodAdaptGUI:
    def __init__(self):

        self.main_path = os.path.dirname(os.path.abspath(__file__))
        self.server_path = os.path.join(self.main_path, "server")

        self.gui = GUI(self,
                       framework="pyqt5",
                       config_file="cfrss.yml",
                       config_path=os.path.join(self.main_path, "config"),
                       server_path=self.server_path,
                       server_port=3000,
                       stylesheet="Combinear.qss",
                       copy_mapbox_server_folder=True)

        # Define variables

        # Define GUI variables


    def on_build(self):
        # Executed after the GUI has been built up (optional)
        pass

    def on_map_ready(self):
        # Executed after the MapBox map has been loaded

        # Find the map widget
        element = find_element_by_id(self.gui.config["element"], "map")
        self.map = element["widget"]

        # Set map view to 55 Columbia Ave in Cranston, RI
        self.map.fly_to(-71.39322, 41.77692, 13)


fa = FloodAdaptGUI()
