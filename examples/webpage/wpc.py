# -*- coding: utf-8 -*-
"""
This is where the application object "wpc" for the webpage application is defined

Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from guitools.gui import GUI

class WebPageComparison:
    def __init__(self):
        self.gui = GUI(self,
                       framework="pyqt5",
                       config_file="webpage.yml",
                       js_messages=False)

wpc = WebPageComparison()
