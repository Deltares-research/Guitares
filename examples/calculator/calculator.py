# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from guitools.gui import GUI


class Calculator:
    def __init__(self):
#        gui_module = __import__(__name__)
        self.gui = GUI(self,
                       framework="pyqt5",
                       splash_file="calculator.jpg",
                       stylesheet="Combinear.qss",
                       config_file="calculator.yml")

    def initialize(self):

        # Define GUI variables
        self.gui.setvar("calculator", "a", 1.0)
        self.gui.setvar("calculator", "b", 2.0)
        self.gui.setvar("calculator", "answer", 3.0)
        self.gui.setvar("calculator", "operator", "plus")
        self.gui.setvar("calculator", "operator_values", ["plus", "minus", "times", "divided_by"])
        self.gui.setvar("calculator", "operator_strings", ["+", "-", "*", "/"])




calculator = Calculator()
