# -*- coding: utf-8 -*-
from ra2ce.ra2ce_handler import Ra2ceHandler
from ra2ceGUI import Ra2ceGUI

import shutil


def modifyRA2CEconfiguration():
    if Ra2ceGUI.valid_input():
        # Load the base network and analyses ini
        _network_ini = Ra2ceGUI.current_project.joinpath('network.ini')
        _analyses_ini = Ra2ceGUI.current_project.joinpath('analyses.ini')

        Ra2ceGUI.ra2ceHandler = Ra2ceHandler(_network_ini, _analyses_ini)

        Ra2ceGUI.update_network_config()
        Ra2ceGUI.update_analyses_config()

        # For now also copy the feather file but it must be made possible to do the analysis without the file base_graph en base_network files!!
        shutil.copy(Ra2ceGUI.loaded_roads, Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                                                              'static',
                                                                                              'output_graph',
                                                                                              'base_graph.p'))
        shutil.copy(Ra2ceGUI.loaded_roads, Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                                                              'static',
                                                                                              'output_graph',
                                                                                              'origins_destinations_graph.p'))
        shutil.copy(Ra2ceGUI.loaded_roads.parent.joinpath('base_network.feather'),
                    Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                                       'static',
                                                                       'output_graph',
                                                                       'base_network.feather'))
        # Update all GUI elements
        Ra2ceGUI.gui.setvar("ra2ceGUI", "valid_config", "Configuration updated")
        Ra2ceGUI.gui.update()
