from ra2ceGUI import Ra2ceGUI
from guitools.pyqt5.io import openFileNameDialog

from pathlib import Path


def validateRA2CEconfiguration():
    print(Ra2ceGUI.selected_floodmap)
    print(Path(Ra2ceGUI.selected_floodmap).is_file())
    pass


def runRA2CE():
    pass


def selectFloodmap():
    Ra2ceGUI.selected_floodmap = openFileNameDialog(Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static', 'hazard'))
    Ra2ceGUI.update_flood_map()
    Ra2ceGUI.gui.setvar("ra2ceGUI", "selected_floodmap", Path(Ra2ceGUI.selected_floodmap).name)

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


def menu_help():
    pass
