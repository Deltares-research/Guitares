# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from guitools.gui import GUI

class MapBoxExample:
    def __init__(self):
#        gui_module = __import__(__name__)
        self.gui = GUI(self,
                       framework="pyqt5",
                       config_file="mapbox_example.yml")
#        self.map = self.gui.map_widget["main_map"]

    def initialize(self):

        # Define GUI variables
        pass

mpbox = MapBoxExample()
