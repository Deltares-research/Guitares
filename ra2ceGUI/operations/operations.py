from ra2ceGUI import Ra2ceGUI
from guitools.pyqt5.io import openFileNameDialog

from pathlib import Path


def selectRoad():
    coords = Ra2ceGUI.gui.getvar("ra2ceGUI", "coords_clicked")
    # Remove the marker from the map after the road has been selected


def openRoads():
    # Get the selected path
    # Ra2ceGUI.loaded_roads = openFileNameDialog(
    #     Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static', 'network'))
    Ra2ceGUI.loaded_roads = Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static',
                                                                                     'network',
                                                                                     f"{Ra2ceGUI.gui.getvar('ra2ceGUI', 'loaded_roads')}.p")

    if Ra2ceGUI.loaded_roads:
        # Find the layer group
        ## TODO: figure out what to do with the selected roads, show in the interface??
        # layer_group = 'Road network'
        # Ra2ceGUI.gui.elements['main_map']['widget_group'].add_layer_group(layer_group)
        #
        # # Add the road network to the map
        # Ra2ceGUI.gui.elements['main_map']['widget_group'].add_line_geojson(Ra2ceGUI.loaded_roads,
        #                                                                    str(Path(Ra2ceGUI.loaded_roads).stem),
        #                                                                    layer_group)

        # Update the text to show underneath the button
        Ra2ceGUI.gui.setvar("ra2ceGUI", "loaded_roads_string", Ra2ceGUI.map_roads_values_strings[Ra2ceGUI.gui.getvar("ra2ceGUI", "loaded_roads")])

        # Update all GUI elements
        Ra2ceGUI.gui.update()


def selectFloodmap():
    Ra2ceGUI.loaded_floodmap = openFileNameDialog(Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static', 'hazard'),
                                                  fileTypes=["GeoTIFF files (*.tif)"])
    if Ra2ceGUI.loaded_floodmap:
        Ra2ceGUI.update_flood_map()
        Ra2ceGUI.gui.setvar("ra2ceGUI", "loaded_floodmap", Path(Ra2ceGUI.loaded_floodmap).name)

        # Update all GUI elements
        Ra2ceGUI.gui.update()
