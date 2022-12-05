# -*- coding: utf-8 -*-
from ra2ceGUI import Ra2ceGUI


def runRA2CE():
    assert Ra2ceGUI.ra2ceHandler

    Ra2ceGUI.ra2ceHandler.configure()
    Ra2ceGUI.ra2ceHandler.run_analysis()
    print("RA2CE successfully ran.")
