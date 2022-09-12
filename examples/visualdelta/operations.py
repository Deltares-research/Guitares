from visualdelta import visualdelta
import pandas as pd
import numpy as np
import os

def add_option():

    # Update all GUI elements
    visualdelta.gui.update()

def change_scenario():
    # Get new value for ssp
    visualdelta.ssp = visualdelta.gui.getvar("visualdelta", "ssp")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()

def change_impact():
    # Get new value for impact
    visualdelta.impact = visualdelta.gui.getvar("visualdelta", "impact")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()

def change_exposure():
    # Get new value for exposure
    visualdelta.exposure = visualdelta.gui.getvar("visualdelta", "exposure")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()

def change_year():
    # Get new value for year
    visualdelta.year = visualdelta.gui.getvar("visualdelta", "year")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()

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

def update_flood_map():

    print("Updating flood map ...")

    image_path = r"d:\temp\van_gundula"

    if visualdelta.slr < 0.2:
        image_file = "flood_withprot_slr=0.00m_rp=0100.tif"
    elif visualdelta.slr < 0.5:
        image_file = "flood_withprot_slr=0.50m_rp=0100.tif"
    else:
        image_file = "flood_withprot_slr=1.00m_rp=0100.tif"

    image_file = os.path.join(image_path, image_file)

    layer_name = "flood_map_layer"
    layer_group_name = "flood_map_layer_group"

    # Add layer group (this only does something when there is no layer group with layer_group_name)
    visualdelta.gui.map_widget["main_map"].add_layer_group(layer_group_name)

    # Remove old layer from layer group
    visualdelta.gui.map_widget["main_map"].remove_layer(layer_name,
                                                        layer_group_name)

    # And now add the new image layer to the layer group
    visualdelta.gui.map_widget["main_map"].add_image_layer(image_file,
                                                           layer_name=layer_name,
                                                           layer_group_name=layer_group_name)

