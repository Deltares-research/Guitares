# -*- coding: utf-8 -*-
from app.ra2ceGUI_base import Ra2ceGUI
from ra2ce.ra2ce_handler import Ra2ceHandler

import logging
import shutil


def modifyRA2CEconfiguration():
    try:
        if Ra2ceGUI.valid_input():
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

            # Load the base network and analyses ini
            _network_ini = Ra2ceGUI.current_project.joinpath('network.ini')
            _analyses_ini = Ra2ceGUI.current_project.joinpath('analyses.ini')

            # First the files must be copied so that they can be found by the ra2ceHandler
            Ra2ceGUI.ra2ceHandler = Ra2ceHandler(_network_ini, _analyses_ini)

            Ra2ceGUI.update_network_config()
            Ra2ceGUI.update_analyses_config()

            # Update all GUI elements
            Ra2ceGUI.gui.setvar("ra2ceGUI", "valid_config", "Configuration updated")
            Ra2ceGUI.gui.update()
    except FileNotFoundError as e:
        logging.warning("File not found: {}".format(e))


def validateRA2CEconfiguration():
    modifyRA2CEconfiguration()

    try:
        assert Ra2ceGUI.ra2ceHandler
    except AssertionError:
        return

    var = "valid_config"

    if Ra2ceGUI.ra2ceHandler.input_config.is_valid_input():
        Ra2ceGUI.valid_config = True
        Ra2ceGUI.gui.setvar("ra2ceGUI", var, "Valid configuration")
    else:
        Ra2ceGUI.valid_config = False
        Ra2ceGUI.gui.setvar("ra2ceGUI", var, "Invalid configuration")

    # Update all GUI elements
    Ra2ceGUI.gui.update()
