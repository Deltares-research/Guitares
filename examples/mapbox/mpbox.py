# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
from guitools.gui import GUI

class MapBoxExample:
    def __init__(self):

        self.main_path = os.path.dirname(os.path.abspath(__file__))
        self.server_path = os.path.join(self.main_path, "server")

        # Define variables
        self.layer_groups = {}

        self.layer_group_names = [] # only used in gui
        self.layer_names       = [] # only used in gui
        self.polygon_names     = [] # only used in gui


        self.gui = GUI(self,
                       framework="pyqt5",
                       config_file="mapbox_example.yml",
                       config_path=self.main_path,
                       server_path=self.server_path,
                       server_port=3000)

        # Define GUI variables
        self.gui.setvar("mpbox", "layer_group", "")
        self.gui.setvar("mpbox", "layer_group_names", self.layer_group_names)

        self.gui.setvar("mpbox", "layer", "")
        self.gui.setvar("mpbox", "layer_names", self.layer_names)

        self.gui.setvar("mpbox", "polygon", 0)
        self.gui.setvar("mpbox", "layer_string", self.polygon_names)

mpbox = MapBoxExample()
