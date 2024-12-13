# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from app import app

def select_map_style(*args):
    map_style = app.gui.getvar("example", "map_style")
    print(f"Map style selected: {map_style}")
    app.map.set_layer_style(map_style)
