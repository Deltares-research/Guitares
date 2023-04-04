from app import app

def select_a(*args):

    print(args)

def select_b(*args):
    print(args)

def select_c(*args):
    c = app.gui.getvar("listboxes", "c")
    app.gui.setvar("listboxes", "d", [c])
    print(args)

def select_d(*args):
    print(args)
