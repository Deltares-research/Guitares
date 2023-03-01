from app import app

def collapse(*args):
    element = app.gui.window.find_element_by_id("dual")
    if element.collapsed:
        element.set_collapsed(False)
    else:
        element.set_collapsed(True)
