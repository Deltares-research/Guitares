from visualdelta import visualdelta
import os

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