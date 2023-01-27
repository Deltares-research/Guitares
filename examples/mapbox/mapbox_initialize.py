# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
import os
from cht.bathymetry.bathymetry_database import bathymetry_database
from colormap import read_colormap
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

def initialize(mpbox):

    # Define variables
    mpbox.layer_groups = {}

    mpbox.layer_group_names = [] # only used in gui
    mpbox.layer_names       = [] # only used in gui
    mpbox.polygon_names     = [] # only used in gui
    mpbox.auto_update_topography = True
    mpbox.background_topography  = "gebco22"
#        mpbox.background_topography  = "new_jersey_delaware_coned_2015"
    mpbox.bathymetry_database_path = "c:\\work\\delftdashboard\\data\\bathymetry"
    bathymetry_database.initialize(mpbox.bathymetry_database_path)

    f = open(os.path.join(mpbox.server_path, "grid.geojson"), "r")
    mpbox.gridjsontxt = f.read()
    f.close()

    rgb = read_colormap('c:/work/checkouts/svn/OET/matlab/applications/DelftDashBoard/settings/colormaps/earth.txt')
    mpbox.color_map_earth = ListedColormap(rgb)

    
    # Define GUI variables
    mpbox.gui.setvar("mpbox", "layer_group", "")
    mpbox.gui.setvar("mpbox", "layer_group_names", mpbox.layer_group_names)
    
    mpbox.gui.setvar("mpbox", "layer", "")
    mpbox.gui.setvar("mpbox", "layer_names", mpbox.layer_names)
    mpbox.gui.setvar("mpbox", "active_layer_id", "")
    
    mpbox.gui.setvar("mpbox", "polygon", 0)
    mpbox.gui.setvar("mpbox", "layer_string", mpbox.polygon_names)


#def initialize_gui_variables(mpbox):
