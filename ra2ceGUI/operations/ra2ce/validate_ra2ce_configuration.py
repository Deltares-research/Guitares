# -*- coding: utf-8 -*-
from ra2ceGUI import Ra2ceGUI


def validateRA2CEconfiguration():
    assert Ra2ceGUI.ra2ceHandler

    var = "valid_config"

    if Ra2ceGUI.ra2ceHandler.input_config.is_valid_input():
        Ra2ceGUI.valid_config = True
        Ra2ceGUI.gui.setvar("ra2ceGUI", var, "Valid configuration")
        Ra2ceGUI.gui.elements['valid_config']['widget_group'].change_background('green')
    else:
        Ra2ceGUI.valid_config = False
        Ra2ceGUI.gui.setvar("ra2ceGUI", var, "Invalid configuration")
        Ra2ceGUI.gui.elements['valid_config']['widget_group'].change_background('red')

    # Update all GUI elements
    Ra2ceGUI.gui.update()
