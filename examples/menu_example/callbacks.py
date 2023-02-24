from app import app

def enter_name(*args):
    name = app.gui.getvar("hello", "name")
    response = "Hello " + name + ", it's nice to meet you!"
    app.gui.setvar("hello", "response", response)
