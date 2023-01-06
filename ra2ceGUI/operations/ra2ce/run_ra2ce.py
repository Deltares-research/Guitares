# -*- coding: utf-8 -*-
from ra2ceGUI import Ra2ceGUI


def analyzeFeedback(text):
    Ra2ceGUI.analyse_feedback = text
    Ra2ceGUI.gui.setvar("ra2ceGUI", "analyse_feedback", Ra2ceGUI.analyse_feedback)

    # Update all GUI elements
    Ra2ceGUI.gui.update()


def runRA2CE():
    try:
        assert Ra2ceGUI.ra2ceHandler
    except AssertionError:
        return

    try:
        assert Ra2ceGUI.floodmap_overlay_feedback == "Overlay done"
    except AssertionError:
        analyzeFeedback("Overlay flood map")
        return

    try:
        # Ra2ceGUI.ra2ceHandler.input_config.network_config.configure_network()
        Ra2ceGUI.ra2ceHandler.input_config.analysis_config.configure()
        Ra2ceGUI.ra2ceHandler.run_analysis()
        print("RA2CE successfully ran.")
    except BaseException as e:
        print(e)
