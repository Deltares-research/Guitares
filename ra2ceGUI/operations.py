from ra2ceGUI import Ra2ceGUI
from guitools.pyqt5.io import openFileNameDialog
from ra2ce.ra2ce_handler import Ra2ceHandler

from pathlib import Path


def selectRoad():
    coords = Ra2ceGUI.gui.getvar("ra2ceGUI", "coords_clicked")
    # Remove the marker from the map after the road has been selected


def openRoads():
    # Get the selected path
    Ra2ceGUI.loaded_roads = openFileNameDialog(
        Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static', 'network'))

    if Ra2ceGUI.loaded_roads:
        # Find the layer group
        layer_group = 'Road network'
        Ra2ceGUI.gui.elements['main_map']['widget_group'].add_layer_group(layer_group)

        # Add the road network to the map
        Ra2ceGUI.gui.elements['main_map']['widget_group'].add_line_geojson(Ra2ceGUI.loaded_roads,
                                                                           str(Path(Ra2ceGUI.loaded_roads).stem),
                                                                           layer_group)

        # Update the text to show underneath the button
        Ra2ceGUI.gui.setvar("ra2ceGUI", "loaded_roads", Path(Ra2ceGUI.loaded_roads).name)

        # Update all GUI elements
        Ra2ceGUI.gui.update()


def getRA2CEConfigFiles():
    network_ini = Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('network.ini')
    analyses_ini = Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('analyses.ini')

    if network_ini.is_file() and analyses_ini.is_file():
        return network_ini, analyses_ini
    elif network_ini.is_file() and not analyses_ini.is_file():
        return network_ini, None
    elif not network_ini.is_file() and analyses_ini.is_file():
        return None, analyses_ini
    else:
        print(f"Both the network and analyses ini files are not found here:\n{network_ini}\n{analyses_ini}")
        return None, None


def getRA2CEHandler():
    _network_ini, _analyses_ini = getRA2CEConfigFiles()
    Ra2ceGUI.ra2ceHandler = Ra2ceHandler(_network_ini, _analyses_ini)


def validateRA2CEconfiguration():
    var = "valid_config"
    getRA2CEHandler()

    if Ra2ceGUI.ra2ceHandler.input_config.is_valid_input():
        Ra2ceGUI.valid_config = True
        Ra2ceGUI.gui.setvar("ra2ceGUI", var, "Valid configuration")
        Ra2ceGUI.gui.elements['valid_config']['widget_group'].change_background('green')
    else:
        Ra2ceGUI.valid_config = False
        Ra2ceGUI.gui.setvar("ra2ceGUI", var, "Invalid configuration")
        Ra2ceGUI.gui.elements['valid_config']['widget_group'].change_background('red')

    # Update all GUI elements
    Ra2ceGUI.gui.update()


def runRA2CE():
    getRA2CEHandler()

    Ra2ceGUI.ra2ceHandler.configure()
    Ra2ceGUI.ra2ceHandler.run_analysis()
    print("RA2CE successfully ran.")


def loadFloodmap():
    Ra2ceGUI.loaded_floodmap = openFileNameDialog(Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static', 'hazard'))
    if Ra2ceGUI.loaded_floodmap:
        Ra2ceGUI.update_flood_map()
        Ra2ceGUI.gui.setvar("ra2ceGUI", "loaded_floodmap", Path(Ra2ceGUI.loaded_floodmap).name)

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
