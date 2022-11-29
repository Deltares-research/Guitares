# -*- coding: utf-8 -*-
from operations.ra2ce.ra2ce_utils import getRA2CEHandler
from ra2ceGUI import Ra2ceGUI


def runRA2CE():
    getRA2CEHandler()

    Ra2ceGUI.ra2ceHandler.configure()
    Ra2ceGUI.ra2ceHandler.run_analysis()
    print("RA2CE successfully ran.")
