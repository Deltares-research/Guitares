from visualdelta import visualdelta
import pandas as pd
import numpy as np
import os
import glob
from geojson import Feature, Point, FeatureCollection

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

def update_flood_map():

    print("Updating flood map ...")

    img_files = os.listdir(os.path.join(visualdelta.main_path,'floodmaps'))
    img_dict = {}
    image_file = os.path.join(visualdelta.main_path,'floodmaps', img_files[0])
    for f in img_files:
        if float(f[19:23]) >= visualdelta.slr:
            image_file = os.path.join(visualdelta.main_path,'floodmaps', f)
            break

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
                                                           layer_group_name=layer_group_name,
                                                           legend_title="Depth (m)",
                                                           colormap="jet",
                                                           cmin=0.2,
                                                           cmax=2.0,
                                                           cstep=0.2,
                                                           decimals=1)

def update_tipping_points():

    print("Updating tipping points ...")

    # Add some markers

    layer_group_name = "tipping_points"
    # Add layer group (this only does something when there is no layer group with layer_group_name)
    visualdelta.gui.map_widget["main_map"].add_layer_group(layer_group_name)

    # Oosterscheldekering
    layer_name = "oosterscheldekering"
    # Remove old layer from layer group
    visualdelta.gui.map_widget["main_map"].remove_layer(layer_name,
                                                        layer_group_name)
    if visualdelta.slr > 0.2:
        properties = {}
        properties = {}
#        properties["hover_popup_text"] = "I'm the Oosterscheldekering!"
        properties["hover_popup_text"]  = "<strong>I'm the Oosterscheldekering!</strong><iframe src=https://www.foxnews.com width=500 height=300></iframe>"
        properties["hover_popup_width"] = 520

        marker = Feature(geometry=Point((3.700, 51.633)), properties=properties)
        visualdelta.gui.map_widget["main_map"].add_marker_layer(FeatureCollection([marker]),
                                                                marker_file="oosterschelde.png",
                                                                layer_name=layer_name,
                                                                layer_group_name=layer_group_name)

    # Maeslantkering
    layer_name = "maeslantkering"
    # Remove old layer from layer group
    visualdelta.gui.map_widget["main_map"].remove_layer(layer_name,
                                                        layer_group_name)
    if visualdelta.slr > 0.5:
        properties = {}
        properties["hover_popup_text"] = "<strong>I'm the Maeslantkering!</strong><p>With this sea level rise, I will have to close very often ...</p>"
        marker = Feature(geometry=Point((4.164, 51.955)), properties=properties)
        visualdelta.gui.map_widget["main_map"].add_marker_layer(FeatureCollection([marker]),
                                                                marker_file="maeslant.png",
                                                                layer_name=layer_name,
                                                                layer_group_name=layer_group_name)
