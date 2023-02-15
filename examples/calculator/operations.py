"""
This is the callback module for the calculator app. The name of this module is defined in the GUI configuration file calculator.yml.
Any the the user interacts with the GUI, it calls methods defined in this module.

The method typically get two input arguments:
 args[0] is the new value of a widget edited/selected by the user.
 args[1] is the object of the widget that was edited/clicked/selected by the user.   
"""

from calc import calc

def calculate(*args):

    # Get inputs from gui variable dict
    a = calc.gui.getvar("calculator", "a")
    b = calc.gui.getvar("calculator", "b")
    operator = calc.gui.getvar("calculator", "operator")

    if operator == "plus":
        answer = a + b
    elif operator == "minus":
        answer = a - b
    elif operator == "times":
        answer = a * b
    elif operator == "divided_by":
        if b == 0.0:
            b = 1.0e-9
        answer = a / b

    calc.gui.setvar("calculator", "answer", answer)
