from ra2ceGUI import Ra2ceGUI
from geojson import Feature, Point, FeatureCollection
import pandas as pd
import os
import numpy as np

def update_tipping_points():

    print("Updating tipping points ...")

    atp = pd.read_csv(os.path.join(Ra2ceGUI.main_path,'atps', 'ATP_database.csv'))

    locations = np.unique(atp.Location)

    # Add some markers

    layer_group_name = "tipping_points"
    # Add layer group (this only does something when there is no layer group with layer_group_name)
    Ra2ceGUI.gui.map_widget["main_map"].add_layer_group(layer_group_name)

    #ToDO: cannot show multiple locations yet (always removes the first location)
    for loc in locations:
        layer_name = loc
        loc_df = atp[atp.Location == loc]
        # Remove old layer from layer group
        Ra2ceGUI.gui.map_widget["main_map"].remove_layer(layer_name,
                                                            layer_group_name)
        atp_limit = None
        for ii, thr in enumerate(loc_df.threshold):
            if Ra2ceGUI.slr > thr:
                atp_limit = thr

        if atp_limit is not None:
            properties = {}
            loc_atp = loc_df[loc_df.threshold==atp_limit]
            properties["hover_popup_text"] = loc + ': ' + loc_atp.Description.item()
    #         properties["hover_popup_text"]  = "<strong>I'm the Oosterscheldekering!</strong><iframe src=https://www.foxnews.com width=500 height=300></iframe>"
            properties["hover_popup_width"] = 520
            marker = Feature(geometry=Point((float(loc_atp.x), float(loc_atp.y))), properties=properties)
            Ra2ceGUI.gui.map_widget["main_map"].add_marker_layer(FeatureCollection([marker]),
                                                                    marker_file=loc_atp.icon_file.item(),
                                                                    layer_name=layer_name,
                                                                    layer_group_name=layer_group_name)
