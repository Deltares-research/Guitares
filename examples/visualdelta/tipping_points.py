from visualdelta import visualdelta
from geojson import Feature, Point, FeatureCollection
import pandas as pd
import os
import numpy as np

def update_tipping_points():

    print("Updating tipping points ...")

    atp = pd.read_csv(os.path.join(visualdelta.main_path,'atps', 'ATP_database.csv'))

    locations = np.unique(atp.Location)

    # Add some markers

    layer_group_name = "tipping_points"
    # Add layer group (this only does something when there is no layer group with layer_group_name)
    visualdelta.gui.map_widget["main_map"].add_layer_group(layer_group_name)

    #ToDO: cannot show multiple locations yet (always removes the first location)
    for loc in locations:
        layer_name = loc
        loc_df = atp[atp.Location == loc]
        # Remove old layer from layer group
        visualdelta.gui.map_widget["main_map"].remove_layer(layer_name,
                                                            layer_group_name)
        atp_limit = None
        for ii, thr in enumerate(loc_df.threshold):
            if visualdelta.slr > thr:
                atp_limit = thr

        if atp_limit is not None:
            properties = {}
            loc_atp = loc_df[loc_df.threshold==atp_limit]
            properties["hover_popup_text"] = loc + ': ' + loc_atp.Description.item()
    #         properties["hover_popup_text"]  = "<strong>I'm the Oosterscheldekering!</strong><iframe src=https://www.foxnews.com width=500 height=300></iframe>"
            properties["hover_popup_width"] = 520
            marker = Feature(geometry=Point((float(loc_atp.x), float(loc_atp.y))), properties=properties)
            visualdelta.gui.map_widget["main_map"].add_marker_layer(FeatureCollection([marker]),
                                                                    marker_file=loc_atp.icon_file.item(),
                                                                    layer_name=layer_name,
                                                                    layer_group_name=layer_group_name)

    # # Maeslantkering
    # layer_name = "Maeslantkering"
    # loc = layer_name
    # loc_df = atp[atp.Location == loc]
    # # Remove old layer from layer group
    # # visualdelta.gui.map_widget["main_map"].remove_layer(layer_name,
    # #                                                     layer_group_name)
    #
    # for ii,thr in enumerate(loc_df.threshold):
    #     if visualdelta.slr > thr:
    #         visualdelta.gui.map_widget["main_map"].remove_layer(layer_name,
    #                                                             layer_group_name)
    #         properties = {}
    #         loc_atp = loc_df[loc_df.threshold==thr]
    #         properties["hover_popup_text"] = loc + ': ' + loc_atp.Description.item()
    # #         properties["hover_popup_text"]  = "<strong>I'm the Oosterscheldekering!</strong><iframe src=https://www.foxnews.com width=500 height=300></iframe>"
    #         properties["hover_popup_width"] = 520
    #
    #         marker = Feature(geometry=Point((float(loc_atp.x), float(loc_atp.y))), properties=properties)
    #         visualdelta.gui.map_widget["main_map"].add_marker_layer(FeatureCollection([marker]),
    #                                                                 marker_file=loc_atp.icon_file.item(),
    #                                                                 layer_name=layer_name,
    #                                                                 layer_group_name=layer_group_name)
    # if visualdelta.slr > 0.5:
    #     properties = {}
    #     properties["hover_popup_text"] = "<strong>I'm the Maeslantkering!</strong><p>With this sea level rise, I will have to close very often ...</p>"
    #     marker = Feature(geometry=Point((4.164, 51.955)), properties=properties)
    #     visualdelta.gui.map_widget["main_map"].add_marker_layer(FeatureCollection([marker]),
    #                                                             marker_file="maeslant.png",
    #                                                             layer_name=layer_name,
    #                                                             layer_group_name=layer_group_name)