# -*- coding: utf-8 -*-


def validateRA2CEconfiguration():
    var = "valid_config"
    getRA2CEHandler()

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
