# -*- coding: utf-8 -*-
from ra2ceGUI.ra2ceGUI_base import Ra2ceGUI


def map_moved(coords):
    print("Map move to :" + str(coords))


def coords_clicked(coords):
    print("Coords clicked: " + str(coords))
    Ra2ceGUI.gui.setvar("ra2ceGUI", "coords_clicked", coords)


