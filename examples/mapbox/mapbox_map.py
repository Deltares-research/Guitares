# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from mpbox import mpbox
from cht.bathymetry.bathymetry_database import bathymetry_database


def map_ready():
    # This method is called when the map has been loaded


    # layer_id = "main.background_topography"
    # mpbox.background_topography_layer = mpbox.gui.map_widget["main_map"].add_layer(layer_id, "raster")
    # mpbox.background_topography_layer.update = update_background

    mpbox.gui.map_widget["main_map"].jump_to(0.0, 0.0, 2)

    layer_id = "main.tiles"
    tile_layer = mpbox.gui.map_widget["main_map"].add_layer(layer_id, "decktile")

#    update_background()

def map_moved(coords):
    # This method is called whenever the location of the map changes
    pass
#    print("Map move to :" + str(coords))


def update_background():
    if not mpbox.gui.map_widget["main_map"].map_extent:
        print("Map extent not yet available ...")
        return
    coords = mpbox.gui.map_widget["main_map"].map_extent
    if mpbox.auto_update_topography:
        xl = [coords[0][0], coords[1][0]]
        yl = [coords[0][1], coords[1][1]]
        dxmax = 900.0
        maxcellsize = (xl[1] - xl[0]) / dxmax
        maxcellsize *= 111111
        try:
            x, y, z = bathymetry_database.get_data(mpbox.background_topography,
                                                   xl,
                                                   yl,
                                                   maxcellsize)
            mpbox.background_topography_layer.set_data(x=x, y=y, z=z,
                                                       colormap=mpbox.color_map_earth,
                                                       decimals=0)
        except:
            print("Error loading background topo ...")
