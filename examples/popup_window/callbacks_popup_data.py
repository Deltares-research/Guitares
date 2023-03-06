from app import app

def on_okay(*args):
    # Okay was pressed
    app.gui.popup_data = app.gui.getvar("popup", "string_in_popup_window")

def edit_text(*args):
    # No need to do anything here
    pass
