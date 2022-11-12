import random

import rasterio
import rasterio.features
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio import MemoryFile

import numpy as np
import matplotlib
import os
from PIL import Image
from matplotlib import cm

from mpbox import mpbox

def add_layer_group():
    name = str(random.randint(0, 1000))
    mpbox.layer_groups[name] = {}
    mpbox.layer_groups[name]["layer"] = {}
    mpbox.layer_group_names = list(mpbox.layer_groups.keys())
    mpbox.gui.setvar("mpbox", "layer_group_names", mpbox.layer_group_names)
    mpbox.gui.setvar("mpbox", "layer_group", mpbox.layer_group_names[-1])
    mpbox.gui.update()

def delete_layer_group():
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    mpbox.layer_groups.pop(layer_group)
    mpbox.layer_group_names = list(mpbox.layer_groups.keys())
    mpbox.gui.setvar("mpbox", "layer_group_names", mpbox.layer_group_names)
    if mpbox.layer_group_names:
        mpbox.gui.setvar("mpbox", "layer_group", mpbox.layer_group_names[-1])
    else:
        mpbox.gui.setvar("mpbox", "layer_group", "")
    mpbox.gui.update()

def select_layer_group():
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    mpbox.layer_names = [""]
    if layer_group:
        # Update layers
        if "layer" in mpbox.layer_groups[layer_group]:
            mpbox.layer_names = list(mpbox.layer_groups[layer_group]["layer"].keys())
        if not mpbox.layer_names:
            mpbox.layer_names = [""]
    layer = mpbox.layer_names[0]
    mpbox.gui.setvar("mpbox", "layer_names", mpbox.layer_names)
    mpbox.gui.setvar("mpbox", "layer", layer)
    mpbox.gui.update()

def add_layer():
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    name = str(random.randint(0, 1000))
    mpbox.layer_groups[layer_group]["layer"][name] = {}
    mpbox.layer_names = list(mpbox.layer_groups[layer_group]["layer"].keys())
    mpbox.gui.setvar("mpbox", "layer_names", mpbox.layer_names)
    mpbox.gui.setvar("mpbox", "layer", mpbox.layer_names[-1])
    mpbox.gui.update()

def add_drawing_layer():
    pass

def add_normal_layer():
    pass

def delete_layer():
    pass

def select_layer():
    pass

def add_polygon():
    # Draw polygon was clicked
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    layer       = mpbox.gui.getvar("mpbox", "layer")
    print("Drawing polygon ...")
    layer_group = mpbox
    mpbox.gui.map_widget["main_map"].draw_polygon(layer, layer_group, create=polygon_created)

def polygon_created(coords):
    print(coords)
def delete_polygon():
    pass

def load_polygon():
    pass

def draw_polygon():
    pass

