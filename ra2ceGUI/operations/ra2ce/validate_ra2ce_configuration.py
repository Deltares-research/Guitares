# -*- coding: utf-8 -*-
from ra2ceGUI import Ra2ceGUI
from ra2ce.ra2ce_handler import Ra2ceHandler

import shutil


def modifyRA2CEconfiguration():
    try:
        if Ra2ceGUI.valid_input():
            # Load the base network and analyses ini
            _network_ini = Ra2ceGUI.current_project.joinpath('network.ini')
            _analyses_ini = Ra2ceGUI.current_project.joinpath('analyses.ini')

            # Copy all required files
            shutil.copy(Ra2ceGUI.origins_destinations_graph, Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                                                                  'static',
                                                                                                  'output_graph',
                                                                                                  'origins_destinations_graph.p'))

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


def validateRA2CEconfiguration():
    modifyRA2CEconfiguration()

    try:
        assert Ra2ceGUI.ra2ceHandler
    except AssertionError:
        Ra2ceGUI.gui.setvar("ra2ceGUI", "valid_config", "First update configuration")
        Ra2ceGUI.gui.update()
        return

    var = "valid_config"

    if Ra2ceGUI.ra2ceHandler.input_config.is_valid_input():
        Ra2ceGUI.valid_config = True
        Ra2ceGUI.gui.setvar("ra2ceGUI", var, "Valid configuration")
        Ra2ceGUI.gui.elements['valid_config']['widget_group'].widgets[0].setStyleSheet("QPushButton{color: green}")
    else:
        Ra2ceGUI.valid_config = False
        Ra2ceGUI.gui.setvar("ra2ceGUI", var, "Invalid configuration")
        Ra2ceGUI.gui.elements['valid_config']['widget_group'].widgets[0].setStyleSheet("QPushButton{color: red}")

    # Update all GUI elements
    Ra2ceGUI.gui.update()
