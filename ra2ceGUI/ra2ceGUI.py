# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
import os
from pathlib import Path

from guitools.gui import GUI
from ra2ce.io.readers.ini_file_reader import IniFileReader


class Ra2ceGUI:
    def __init__(self):
#        gui_module = __import__(__name__)

        self.main_path = os.path.dirname(os.path.abspath(__file__))

        # Read the additional ini file (for RA2CE)
        self.ra2ce_ini = Path(self.main_path).joinpath('ra2ce.ini')
        self.ra2ce_config = IniFileReader().read(self.ra2ce_ini)

        server_path = os.path.join(self.main_path, "server")
        self.server_path = server_path

        # Initialize a RA2CE handler
        self.ra2ceHandler = None

        self.gui = GUI(self,
                       framework="pyqt5",
                       splash_file="ra2ceGUI.jpg",
                       config_file="ra2ceGUI.yml",
                       stylesheet="Combinear.qss",
                       config_path=self.main_path,
                       server_path=server_path,
                       server_port=3000)

    def initialize(self):
        # Define variables
        self.loaded_floodmap = "Not yet selected"
        self.loaded_roads_values = ["markets_residential", "warehouses_shelters", "shelters_hospitals"]
        self.loaded_roads_strings = ["Markets -> Residential homes", "Food warehouses -> Shelters", "Shelters -> Hospitals"]
        self.map_roads_values_strings = dict(zip(self.loaded_roads_values, self.loaded_roads_strings))
        self.loaded_roads = self.loaded_roads_values[0]
        self.loaded_roads_string = self.loaded_roads_strings[0]
        self.valid_config = "Not yet configured"
        self.coords_clicked = None

        # Define GUI variables
        self.gui.setvar("ra2ceGUI", "loaded_floodmap", self.loaded_floodmap)
        self.gui.setvar("ra2ceGUI", "loaded_roads", self.loaded_roads)
        self.gui.setvar("ra2ceGUI", "loaded_roads_string", self.loaded_roads_string)
        self.gui.setvar("ra2ceGUI", "loaded_roads_values", self.loaded_roads_values)
        self.gui.setvar("ra2ceGUI", "loaded_roads_strings", self.loaded_roads_strings)
        self.gui.setvar("ra2ceGUI", "threshold_road_disruption", 0.)  # 0 as default value?
        self.gui.setvar("ra2ceGUI", "valid_config", self.valid_config)
        self.gui.setvar("ra2ceGUI", "coords_clicked", self.coords_clicked)

    def update_flood_map(self):
        layer_name = Path(self.loaded_floodmap).name
        layer_group_name = "flood_map_layer_group"

        # Add layer group (this only does something when there is no layer group with layer_group_name)
        self.gui.map_widget["main_map"].add_layer_group(layer_group_name)

        # Remove old layer from layer group
        self.gui.map_widget["main_map"].remove_layer(layer_name, layer_group_name)

        # And now add the new image layer to the layer group
        self.gui.map_widget["main_map"].add_image_layer(Ra2ceGUI.loaded_floodmap,
                                                            layer_name=layer_name,
                                                            layer_group_name=layer_group_name,
                                                            legend_title="Depth (m)",
                                                            colormap="jet",
                                                            cmin=0.2,
                                                            cmax=2.0,
                                                            cstep=0.2,
                                                            decimals=1)


Ra2ceGUI = Ra2ceGUI()
