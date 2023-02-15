from mpbox import mpbox

def select(*args):
    # Set map view to 55 Columbia Ave in Cranston, RI
    mpbox.map.fly_to(-71.39322, 41.77692, 13)

def add_draw_layers():

    layer = mpbox.map.layer["main"]

    layer.add_draw_layer("polygon_layer",
                         shape="polygon",
                         create=polygon_created,
                         modify=polygon_modified,
                         select=polygon_selected,
                         polygon_line_color="limegreen",
                         polygon_fill_color="limegreen",
                         polygon_fill_opacity=0.3)

    layer.add_draw_layer("polyline_layer",
                         shape="polyline",
                         create=polyline_created,
                         modify=polyline_modified,
                         select=polyline_selected)


def draw_polygon(*args):
    mpbox.map.layer["main"].layer["polygon_layer"].draw()

def delete_polygon(*args):
    if len(mpbox.polygons) == 0:
        return
    index = mpbox.gui.getvar("mpbox", "polygon_index")
    # or: iac = args[0]
    feature_id = mpbox.polygons.loc[index, "id"]
    # Delete from map
    mpbox.map.layer["main"].layer["polygon_layer"].delete_feature(feature_id)
    # Delete from app
    mpbox.polygons = mpbox.polygons.drop(index)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(mpbox.polygons) - 1:
        mpbox.gui.setvar("mpbox", "polygon_index", len(mpbox.polygons) - 1)

    update()

def select_polygon(*args):
    # From GUI
    index = args[0]
    feature_id = mpbox.polygons.loc[index, "id"]
    mpbox.map.layer["main"].layer["polygon_layer"].activate_feature(feature_id)

def polygon_created(gdf, index, id):
    mpbox.polygons = gdf
    mpbox.gui.setvar("mpbox", "polygon_index", index)
    update()

def polygon_modified(gdf, index, id):
    mpbox.polygons = gdf
    mpbox.gui.setvar("mpbox", "polygon_index", index)
    update()

def polygon_selected(index):
    # From map
    mpbox.gui.setvar("mpbox", "polygon_index", index)
    update()


def draw_polyline(*args):
    mpbox.map.layer["main"].layer["polyline_layer"].draw()

def delete_polyline(*args):
    if len(mpbox.polylines) == 0:
        return
    index = mpbox.gui.getvar("mpbox", "polyline_index")
    # or: iac = args[0]
    feature_id = mpbox.polylines.loc[index, "id"]
    # Delete from map
    mpbox.map.layer["main"].layer["polyline_layer"].delete_feature(feature_id)
    # Delete from app
    mpbox.polylines = mpbox.polylines.drop(index)
    if index > len(mpbox.polylines) - 1:
        mpbox.gui.setvar("mpbox", "polyline_index", len(mpbox.polylines) - 1)
    update()

def select_polyline(*args):
    # From GUI
    index = args[0]
    feature_id = mpbox.polylines.loc[index, "id"]
    mpbox.map.layer["main"].layer["polyline_layer"].activate_feature(feature_id)

def polyline_created(gdf, index, id):
    mpbox.polylines = gdf
    mpbox.gui.setvar("mpbox", "polyline_index", index)
    update()

def polyline_modified(gdf, index, id):
    mpbox.polylines = gdf
    mpbox.gui.setvar("mpbox", "polyline_index", index)
    update()

def polyline_selected(index):
    # From map
    mpbox.gui.setvar("mpbox", "polyline_index", index)
    update()

def update():

    polygon_names = []
    for i in range(len(mpbox.polygons)):
        polygon_names.append("polygon" + str(i + 1))
    mpbox.gui.setvar("mpbox", "polygon_names", polygon_names)
    mpbox.gui.setvar("mpbox", "nr_polygons", len(mpbox.polygons))

    polyline_names = []
    for i in range(len(mpbox.polylines)):
        polyline_names.append("polyline" + str(i + 1))
    mpbox.gui.setvar("mpbox", "polyline_names", polyline_names)
    mpbox.gui.setvar("mpbox", "nr_polylines", len(mpbox.polylines))

    mpbox.gui.update()

