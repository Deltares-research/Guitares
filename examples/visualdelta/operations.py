from visualdelta import visualdelta
import pandas as pd
import numpy as np
import os
from tipping_points import update_tipping_points
from maps import update_flood_map

def change_scenario():
    # Get new value for ssp
    visualdelta.ssp = visualdelta.gui.getvar("visualdelta", "ssp")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()
    update_tipping_points()

def change_impact():
    # Get new value for impact
    visualdelta.impact = visualdelta.gui.getvar("visualdelta", "impact")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()
    update_tipping_points()

def change_exposure():
    # Get new value for exposure
    visualdelta.exposure = visualdelta.gui.getvar("visualdelta", "exposure")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()
    update_tipping_points()

def change_year():
    # Get new value for year
    visualdelta.year = visualdelta.gui.getvar("visualdelta", "year")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()
    update_tipping_points()

def change_year_slider():
    # This method is called while the slider is being moved
    visualdelta.year = visualdelta.gui.getvar("visualdelta", "year")
    calculate_slr()

def calculate_slr():
    # Compute SLR
    csv_file = os.path.join(visualdelta.main_path, "slr", 'SLR_{}.csv'.format(visualdelta.ssp))
    slr_ts = pd.read_csv(csv_file, index_col=0, header=0)
    slr_val = np.interp(visualdelta.year, slr_ts.index, slr_ts['0.5'])
    slr_low = np.interp(visualdelta.year, slr_ts.index, slr_ts['0.17'])
    slr_high = np.interp(visualdelta.year, slr_ts.index, slr_ts['0.83'])
    visualdelta.slr = round(slr_val, 2)
    visualdelta.gui.setvar("visualdelta", "slr_string", str(visualdelta.slr) + " m")
    # visualdelta.gui.setvar("visualdelta", "slr_string", "{} m ({} - {} m)".format(round(slr_val, 2),
    #                                                                               round(slr_low, 2),
    #                                                                               round(slr_high, 2)))

    # Update all GUI elements
    visualdelta.gui.update()

def draw_polygon():
    visualdelta.gui.map_widget["main_map"].draw_polygon("layer1",
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
    visualdelta.gui.map_widget["main_map"].draw_polyline("layer1",
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
    visualdelta.gui.map_widget["main_map"].draw_rectangle("layer1",
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
