# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from app import app

def map_ready(widget):
    # This method is called when the map has been loaded
    print('Map is ready !')
    app.map = widget

    app.initialize()
 
def map_moved(coords, widget):
    # This method is called whenever the location of the map changes
    print('Map has moved to:', coords)
