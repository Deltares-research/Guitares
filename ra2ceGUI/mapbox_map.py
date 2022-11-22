# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
from ra2ceGUI import Ra2ceGUI


def map_moved(coords):
    print("Map move to :" + str(coords))


def coords_clicked(coords):
    print("Coords clicked: " + str(coords))
    Ra2ceGUI.gui.setvar("ra2ceGUI", "coords_clicked", coords)


