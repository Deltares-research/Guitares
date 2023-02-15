# -*- coding: utf-8 -*-
"""
This is where the application object "calc" for the calculator application is defined

Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from guitools.gui import GUI

class Calculator:
    def __init__(self):

        self.gui = GUI(self,
                       framework="pyqt5",
                       splash_file="calculator.jpg",
                       stylesheet="Combinear.qss",
                       config_file="calculator.yml")

        # Define GUI variables
        self.gui.setvar("calculator", "a", 1.0)
        self.gui.setvar("calculator", "b", 2.0)
        self.gui.setvar("calculator", "answer", 3.0)
        self.gui.setvar("calculator", "operator", "plus")
        self.gui.setvar("calculator", "operator_values", ["plus", "minus", "times", "divided_by"])
        self.gui.setvar("calculator", "operator_strings", ["+", "-", "*", "/"])

calc = Calculator()
