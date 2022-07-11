from calculator_gui import getvar, setvar, gui


def calculate():
    a = getvar("calculator", "a")
    b = getvar("calculator", "b")
    operator = getvar("calculator", "operator")

    if operator == "plus":
        answer = a + b
    elif operator == "minus":
        answer = a - b
    elif operator == "times":
        answer = a * b
    elif operator == "divided_by":
        answer = a / b
#        gui.olmap["main_map"].add_layer("new_layer", "base")
        gui.olmap["main_map"].draw_polygon("layer1",
                                           create=add_polygon,
                                           modify=modify_polygon)

    setvar("calculator", "answer", answer)

    # Update all GUI elements
    gui.update()


def add_polygon(polid, coords):
    print("Added")
    print(polid)
    print(coords)


def modify_polygon(polid, coords):
    print("Modified")
    print(polid)
    print(coords)

# polygon = None
# gui.olmap["main_map"].add_layer("new_layer", "base")
#gui.olmap["main_map"].delete_layer("new_layer")

#p = gui.olmap["main_map"].add_polygon(polygon, "new_layer")
#gui.olmap["main_map"].delete_polygon(polygon, "new_layer")
