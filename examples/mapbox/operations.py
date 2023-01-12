import random

import rasterio
import rasterio.features
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio import MemoryFile
from PyQt5 import QtCore

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

    mpbox.gui.map_widget["main_map"].add_layer_group(name)

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

    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    layer       = mpbox.gui.getvar("mpbox", "layer")
    layer_id    = layer_group + "." + layer
    mpbox.gui.setvar("mpbox", "active_layer_id", layer_id)
    mpbox.gui.map_widget["main_map"].activate_layer(layer_id)


def add_draw_layer():
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    name = str(random.randint(0, 1000))
    mpbox.layer_groups[layer_group]["layer"][name] = {}
    mpbox.layer_groups[layer_group]["layer"][name]["polygon"] = []
    mpbox.layer_names = list(mpbox.layer_groups[layer_group]["layer"].keys())
    mpbox.gui.setvar("mpbox", "layer_names", mpbox.layer_names)
    mpbox.gui.setvar("mpbox", "layer", mpbox.layer_names[-1])
    layer_id = layer_group + "." + name
    mpbox.gui.setvar("mpbox", "active_layer_id", layer_id)
    mpbox.gui.update()
    mpbox.gui.map_widget["main_map"].add_layer(layer_id, "draw",
                                               create=polygon_created,
                                               modify=polygon_modified)

def add_image_layer():
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    name = str(random.randint(0, 1000))
    mpbox.layer_groups[layer_group]["layer"][name] = {}
    mpbox.layer_groups[layer_group]["layer"][name]["polygon"] = []
    mpbox.layer_names = list(mpbox.layer_groups[layer_group]["layer"].keys())
    mpbox.gui.setvar("mpbox", "layer_names", mpbox.layer_names)
    mpbox.gui.setvar("mpbox", "layer", mpbox.layer_names[-1])
    layer_id = layer_group + "." + name
    mpbox.gui.setvar("mpbox", "active_layer_id", layer_id)
    mpbox.gui.update()

    mpbox.gui.map_widget["main_map"].add_layer(layer_id, "image")

def set_image():
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    layer_name  = mpbox.gui.getvar("mpbox", "layer")
    layer_id    = layer_group + "." + layer_name
    image_file = "c:\\work\\checkouts\\git\\GUITools\\examples\\visualdelta\\floodmaps\\flood_withprot_slr=1.25m_rp=0100.tif"
    mpbox.gui.map_widget["main_map"].set_image(layer_id,
                  image_file=image_file,
                  legend_title="",
                  cmin=0.0,
                  cmax=2.0,
                  cstep=0.1,
                  decimals=1,
                  colormap="jet")


def delete_layer():
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    layer       = mpbox.gui.getvar("mpbox", "layer")
    if layer:
        layer_id    = layer_group + "." + layer
        mpbox.gui.map_widget["main_map"].delete_layer(layer_id)
        mpbox.layer_groups[layer_group]["layer"].pop(layer)
        mpbox.layer_names = list(mpbox.layer_groups[layer_group]["layer"].keys())
        mpbox.gui.setvar("mpbox", "layer_names", mpbox.layer_names)
        if mpbox.layer_names:
            mpbox.gui.setvar("mpbox", "layer", mpbox.layer_names[-1])
            mpbox.gui.setvar("mpbox", "active_layer_id", layer_id)
        else:
            mpbox.gui.setvar("mpbox", "layer", "")
            mpbox.gui.setvar("mpbox", "active_layer_id", "")
        mpbox.gui.update()

        layer       = mpbox.gui.getvar("mpbox", "layer")
        layer_id    = layer_group + "." + layer
        mpbox.gui.map_widget["main_map"].activate_layer(layer_id)


def select_layer():
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    layer       = mpbox.gui.getvar("mpbox", "layer")
    layer_id    = layer_group + "." + layer
    mpbox.gui.setvar("mpbox", "active_layer_id", layer_id)
    mpbox.gui.map_widget["main_map"].activate_layer(layer_id)


def add_polygon():
    # Draw polygon was clicked
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    layer       = mpbox.gui.getvar("mpbox", "layer")
    layer_id = layer_group + "." + layer
    mpbox.gui.map_widget["main_map"].draw_polygon(layer_id)


def polygon_created(feature):
#    print("Polygon created")
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    layer_name  = mpbox.gui.getvar("mpbox", "layer")
    layer = mpbox.layer_groups[layer_group]["layer"][layer_name]
    layer["polygon"].append(feature)

def polygon_modified(feature):
#    print("Polygon modified")
    feature_id = feature["id"][0]
    layer_group = mpbox.gui.getvar("mpbox", "layer_group")
    layer_name  = mpbox.gui.getvar("mpbox", "layer")
    layer = mpbox.layer_groups[layer_group]["layer"][layer_name]
    for pol in layer["polygon"]:
        if pol["id"][0] == feature_id:
            pol["geometry"] = feature["geometry"]
            break


def delete_polygon():
    pass


def load_polygon():
    pass


def draw_polygon():
    pass
