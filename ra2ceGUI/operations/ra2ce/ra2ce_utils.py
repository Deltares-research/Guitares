# -*- coding: utf-8 -*-
from ra2ce.ra2ce_handler import Ra2ceHandler
from ra2ceGUI import Ra2ceGUI

from pathlib import Path


def getRA2CEConfigFiles():
    network_ini = Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('network.ini')
    analyses_ini = Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('analyses.ini')

    if network_ini.is_file() and analyses_ini.is_file():
        return network_ini, analyses_ini
    elif network_ini.is_file() and not analyses_ini.is_file():
        return network_ini, None
    elif not network_ini.is_file() and analyses_ini.is_file():
        return None, analyses_ini
    else:
        print(f"Both the network and analyses ini files are not found here:\n{network_ini}\n{analyses_ini}")
        return None, None


def getRA2CEHandler():
    _network_ini, _analyses_ini = getRA2CEConfigFiles()
    Ra2ceGUI.ra2ceHandler = Ra2ceHandler(_network_ini, _analyses_ini)
