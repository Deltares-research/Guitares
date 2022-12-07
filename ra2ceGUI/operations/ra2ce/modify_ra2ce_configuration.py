# -*- coding: utf-8 -*-
from operations.ra2ce.ra2ce_utils import getRA2CEConfigFiles
from ra2ce.ra2ce_handler import Ra2ceHandler
from ra2ceGUI import Ra2ceGUI


def modifyRA2CEconfiguration():
    if Ra2ceGUI.valid_input():
        # Load the base network and analyses ini
        _network_ini = Ra2ceGUI.current_project.joinpath('network.ini')
        _analyses_ini = Ra2ceGUI.current_project.joinpath('analyses.ini')

        Ra2ceGUI.ra2ceHandler = Ra2ceHandler(_network_ini, _analyses_ini)

        Ra2ceGUI.update_network_config()
        Ra2ceGUI.update_analyses_config()

        # Update all GUI elements
        Ra2ceGUI.gui.setvar("ra2ceGUI", "valid_config", "Configuration updated")
        Ra2ceGUI.gui.update()
