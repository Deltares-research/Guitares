from app import app

def push_simple(*args):
    # Make pop-up window
    app.gui.setvar("popup", "string_in_popup_window", "What?!")
    okay = app.gui.popup("popup_simple.yml")
    if okay:
        response = app.gui.getvar("popup", "string_in_popup_window")        
        app.gui.setvar("main", "response", response)

def push_data(*args):
    # Make pop-up window
    data = "DATA"
    app.gui.setvar("popup", "string_in_popup_window", data)
    okay, data = app.gui.popup("popup_data.yml", data=data)
    if okay:
        app.gui.setvar("main", "response", data)
