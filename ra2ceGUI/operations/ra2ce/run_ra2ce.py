# -*- coding: utf-8 -*-

def runRA2CE():
    getRA2CEHandler()

    Ra2ceGUI.ra2ceHandler.configure()
    Ra2ceGUI.ra2ceHandler.run_analysis()
    print("RA2CE successfully ran.")