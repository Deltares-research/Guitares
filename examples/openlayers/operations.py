from openlayers_test import olt

def draw_polygon():
    olt.gui.olmap["main_map"].draw_polygon("layer1",
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
    olt.gui.olmap["main_map"].draw_polyline("layer1",
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
    olt.gui.olmap["main_map"].draw_rectangle("layer1",
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
