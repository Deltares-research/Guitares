from calculator import calculator


def calculate():

    a = calculator.gui.getvar("calculator", "a")
    b = calculator.gui.getvar("calculator", "b")
    operator = calculator.gui.getvar("calculator", "operator")

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

    calculator.gui.setvar("calculator", "answer", answer)

    # Update all GUI elements
    calculator.gui.update()
