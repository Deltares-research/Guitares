# -*- coding: utf-8 -*-
from ra2ceGUI import Ra2ceGUI


def runRA2CE():
    try:
        assert Ra2ceGUI.ra2ceHandler
    except AssertionError:
        return

    try:
        # Ra2ceGUI.ra2ceHandler.input_config.network_config.configure_network()
        Ra2ceGUI.ra2ceHandler.input_config.analysis_config.configure()
        Ra2ceGUI.ra2ceHandler.run_analysis()
        print("RA2CE successfully ran.")
    except BaseException as e:
        print(e)
