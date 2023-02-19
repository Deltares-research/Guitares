from app import app

def tick_button(*args):
    val = args[0]
    response = "Button " + str(val) + " is checked"
    app.gui.setvar("radiobutton", "response", response)
