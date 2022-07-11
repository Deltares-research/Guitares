# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from guitools.gui import GUI


class WebPageComparison:
    def __init__(self):
        self.gui = GUI(self,
                       framework="pyqt5",
                       config_file="webpage_example.yml")

    def initialize(self):
        pass


wpc = WebPageComparison()
