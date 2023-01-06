# -*- coding: utf-8 -*-
from ra2ceGUI import Ra2ceGUI


def floodMapOverlay():
    try:
        assert Ra2ceGUI.ra2ceHandler
    except AssertionError:
        return

    try:
        Ra2ceGUI.ra2ceHandler.input_config.network_config.configure_hazard()
    except BaseException as e:
        print(e)
