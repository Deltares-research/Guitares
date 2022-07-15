# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from src.guitools.gui import GUI


class VisualDelta:
    def __init__(self):
#        gui_module = __import__(__name__)
        self.gui = GUI(self,
                       framework="pyqt5",
                       splash_file="visualdelta.jpg",
                       stylesheet="Combinear.qss",
                       config_file="visualdelta.yml")

    def initialize(self):

        # Define GUI variables
        self.gui.setvar("visualdelta", "a", 1.0)
        self.gui.setvar("visualdelta", "b", 2.0)
        self.gui.setvar("visualdelta", "answer", 3.0)
        # self.gui.setvar("visualdelta", "operator", "SSP1-2.6")
        # self.gui.setvar("visualdelta", "operator_values", ["plus", "minus", "times", "divided_by"])
        # self.gui.setvar("visualdelta", "operator_strings", ["+", "-", "*", "/"])
        self.gui.setvar("visualdelta", "ssp", "SSP2-4.5")
        self.gui.setvar("visualdelta", "ssp_values", ["SSP1-1.9", "SSP1-2.6", "SSP2-4.5", "SSP3-7.0", "SSP5-8.5"])
        self.gui.setvar("visualdelta", "ssp_strings", ["SSP1-1.9", "SSP1-2.6", "SSP2-4.5", "SSP3-7.0", "SSP5-8.5"])


visualdelta = VisualDelta()
