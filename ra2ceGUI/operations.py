from ra2ceGUI import Ra2ceGUI
import pandas as pd
import numpy as np
import os
from tipping_points import update_tipping_points
from maps import update_flood_map


def change_scenario():
    # Get new value for ssp
    Ra2ceGUI.ssp = Ra2ceGUI.gui.getvar("ra2ceGUI", "ssp")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()
    update_tipping_points()


def change_impact():
    # Get new value for impact
    Ra2ceGUI.impact = Ra2ceGUI.gui.getvar("ra2ceGUI", "impact")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()
    update_tipping_points()


def change_exposure():
    # Get new value for exposure
    Ra2ceGUI.exposure = Ra2ceGUI.gui.getvar("ra2ceGUI", "exposure")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()
    update_tipping_points()


def change_year():
    # Get new value for year
    Ra2ceGUI.year = Ra2ceGUI.gui.getvar("ra2ceGUI", "year")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()
    update_tipping_points()


def change_year_slider():
    # This method is called while the slider is being moved
    Ra2ceGUI.year = Ra2ceGUI.gui.getvar("ra2ceGUI", "year")
    calculate_slr()


def calculate_slr():
    # Compute SLR
    csv_file = os.path.join(Ra2ceGUI.main_path, "slr", 'SLR_{}.csv'.format(Ra2ceGUI.ssp))
    slr_ts = pd.read_csv(csv_file, index_col=0, header=0)
    slr_val = np.interp(Ra2ceGUI.year, slr_ts.index, slr_ts['0.5'])
    slr_low = np.interp(Ra2ceGUI.year, slr_ts.index, slr_ts['0.17'])
    slr_high = np.interp(Ra2ceGUI.year, slr_ts.index, slr_ts['0.83'])
    Ra2ceGUI.slr = round(slr_val, 2)
    Ra2ceGUI.gui.setvar("ra2ceGUI", "slr_string", str(Ra2ceGUI.slr) + " m")
    # Ra2ceGUI.gui.setvar("ra2ceGUI", "slr_string", "{} m ({} - {} m)".format(round(slr_val, 2),
    #                                                                               round(slr_low, 2),
    #                                                                               round(slr_high, 2)))

    # Update all GUI elements
    Ra2ceGUI.gui.update()


def draw_polygon():
    Ra2ceGUI.gui.map_widget["main_map"].draw_polygon("layer1",
                                       create=add_polygon,
                                       modify=modify_polygon)


def add_polygon(polid, coords):
    print("Polygon added")
    print(polid)
    print(coords)


def modify_polygon(polid, coords):
    print("Polygon modified")
    print(polid)
    print(coords)


def draw_polyline():
    Ra2ceGUI.gui.map_widget["main_map"].draw_polyline("layer1",
                                       create=add_polyline,
                                       modify=modify_polyline)


def add_polyline(polid, coords):
    print("Polyline added")
    print("ID= " + str(polid))
    print("Coords = " + str(coords))


def modify_polyline(polid, coords):
    print("Polyline modified")
    print("ID= " + str(polid))
    print("Coords = " + str(coords))


def draw_rectangle():
    Ra2ceGUI.gui.map_widget["main_map"].draw_rectangle("layer1",
                                             create=add_rectangle,
                                             modify=modify_rectangle)


def add_rectangle(polid, coords):
    print("Rectangle added")
    print("ID= " + str(polid))
    print("Coords = " + str(coords))


def modify_rectangle(polid, coords):
    print("Rectangle modified")
    print("ID= " + str(polid))
    print("Coords = " + str(coords))

