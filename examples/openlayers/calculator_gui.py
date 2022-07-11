# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from guitools.gui import GUI

def setvar(group, name, value):
    if group not in gui.variables:
        gui.variables[group] = {}
    if name not in gui.variables[group]:
        gui.variables[group][name] = {}
    gui.variables[group][name]["value"] = value

def getvar(group, name):
    if group not in gui.variables:
        print("Error! GUI variable group '" + group + "' not defined !")
    elif name not in gui.variables[group]:    
        print("Error! GUI variable '" + name + "' not defined in group '" + group + "'!")        
    return gui.variables[group][name]["value"]

gui_module = __import__(__name__)
gui = GUI(gui_module,
          framework="pyqt5",
          splash_file="DelftDashBoard.jpg")
