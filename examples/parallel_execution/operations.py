"""
This is the callback module for the calculator app. The name of this module is defined in the GUI configuration file calculator.yml.
Any the the user interacts with the GUI, it calls methods defined in this module.

The method typically get two input arguments:
 args[0] is the new value of a widget edited/selected by the user.
 args[1] is the object of the widget that was edited/clicked/selected by the user.   
"""

from calc import calc
import time
from guitares.parallel_runner import ParallelRunner


class Calculator:
    def __init__(self):
        calc.gui.setvar("calculator", "calculator_task_status", "Hoi")

    def calculate(self, *args):
        a = calc.gui.getvar("calculator", "a")
        b = calc.gui.getvar("calculator", "b")
        operator = calc.gui.getvar("calculator", "operator")

        runner = ParallelRunner(calc.gui, print_debug = False)
        runner.submit_task(self._do_calculation, a, b, operator, task_name = "calculator_task", write_result=True, group="calculator", name="answer")

    def calculate_parallel(self, *args):
        a = calc.gui.getvar("calculator", "a")
        b = calc.gui.getvar("calculator", "b")
        operator = calc.gui.getvar("calculator", "operator")

        runner = ParallelRunner(calc.gui, print_debug = False)
        runner.submit_parallel_task(self._do_calculation, a, b, operator, task_name = "calculator_task", write_result=True, group="calculator", name="answer")
        
    def _do_calculation(self, a, b, operator):
        # Simulate a long-running calculation
        time.sleep(5)

        if operator == "plus":
            return a + b
        elif operator == "minus":
            return a - b
        elif operator == "times":
            return a * b
        elif operator == "divided_by":
            if b == 0.0:
                b = 1.0e-9
            return a / b