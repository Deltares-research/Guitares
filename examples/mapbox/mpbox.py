# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
from guitools.gui import GUI

from mapbox_initialize import initialize

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
                       stylesheet="Combinear.qss")

        initialize(self)

    def on_build(self):
        pass

mpbox = MapBoxExample()
