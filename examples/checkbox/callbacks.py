from app import app

def tick_box(*args):
    is_checked = app.gui.getvar("checkbox", "checked")
    if is_checked: 
        response = "The box is checked."
    else:
        response = "The box is NOT checked."
    app.gui.setvar("checkbox", "response", response)
