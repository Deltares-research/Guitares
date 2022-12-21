# -*- coding: utf-8 -*-
from ra2ce.ra2ce_handler import Ra2ceHandler
from ra2ceGUI import Ra2ceGUI

import shutil


def modifyRA2CEconfiguration():
    try:
        if Ra2ceGUI.valid_input():
            # Load the base network and analyses ini
            _network_ini = Ra2ceGUI.current_project.joinpath('network.ini')
            _analyses_ini = Ra2ceGUI.current_project.joinpath('analyses.ini')

            # Copy all required files
            shutil.copy(Ra2ceGUI.base_graph, Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                                                                  'static',
                                                                                                  'output_graph',
                                                                                                  'base_graph.p'))
            shutil.copy(Ra2ceGUI.origins_destinations_graph, Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                                                                  'static',
                                                                                                  'output_graph',
                                                                                                  'origins_destinations_graph.p'))
            shutil.copy(Ra2ceGUI.base_network.parent.joinpath('base_network.feather'),
                        Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                                           'static',
                                                                           'output_graph',
                                                                           'base_network.feather'))

            shutil.copy(Ra2ceGUI.origin_destination_table,
                        Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                                           'static',
                                                                           'output_graph',
                                                                           'origin_destination_table.feather'))

            # First the files must be copied so they can be found by the ra2ceHandler
            Ra2ceGUI.ra2ceHandler = Ra2ceHandler(_network_ini, _analyses_ini)

            Ra2ceGUI.update_network_config()
            Ra2ceGUI.update_analyses_config()

            # Update all GUI elements
            Ra2ceGUI.gui.setvar("ra2ceGUI", "valid_config", "Configuration updated")
            Ra2ceGUI.gui.update()
    except FileNotFoundError:
        print("File not found")
