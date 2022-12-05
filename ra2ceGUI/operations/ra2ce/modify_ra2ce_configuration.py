# -*- coding: utf-8 -*-
from operations.ra2ce.ra2ce_utils import getRA2CEConfigFiles
from ra2ce.ra2ce_handler import Ra2ceHandler
from ra2ceGUI import Ra2ceGUI

from pathlib import Path
import shutil


def copy_ini_files():
    base_network_ini = Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static',
                                                                                'ini_template',
                                                                                'network.ini')
    current_network_ini = Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('network.ini')
    base_analyses_ini = Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static',
                                                                                 'ini_template',
                                                                                 'analyses.ini')
    current_analyses_ini = Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('analyses.ini')

    shutil.copy(base_network_ini, current_network_ini)
    shutil.copy(base_analyses_ini, current_analyses_ini)
    return current_network_ini, current_analyses_ini


def valid_input():
    if Path(Ra2ceGUI.loaded_floodmap).is_file() and Ra2ceGUI.gui.getvar("ra2ceGUI", "run_name") != "Choose a name for this run":
        return True
    else:
        if not Path(Ra2ceGUI.loaded_floodmap).is_file() and Ra2ceGUI.gui.getvar("ra2ceGUI", "run_name") != "Choose a name for this run":
            Ra2ceGUI.gui.setvar("ra2ceGUI", "valid_config", "Select a flood map")
        elif Path(Ra2ceGUI.loaded_floodmap).is_file() and Ra2ceGUI.gui.getvar("ra2ceGUI", "run_name") == "Choose a name for this run":
            Ra2ceGUI.gui.setvar("ra2ceGUI", "valid_config", "Provide a run name")
        elif not Path(Ra2ceGUI.loaded_floodmap).is_file() and Ra2ceGUI.gui.getvar("ra2ceGUI", "run_name") == "Choose a name for this run":
            Ra2ceGUI.gui.setvar("ra2ceGUI", "valid_config", "Provide a run name and select a flood map")
        Ra2ceGUI.gui.update()


def modifyRA2CEconfiguration():
    if valid_input():

        _network_ini, _analyses_ini = copy_ini_files()

        # Load the base network and analyses ini
        _network_ini, _analyses_ini = getRA2CEConfigFiles(_network_ini, _analyses_ini)
        Ra2ceGUI.ra2ceHandler = Ra2ceHandler(_network_ini, _analyses_ini)

        # Update the Network ini configurations
        # Project
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['project']['name'] = Ra2ceGUI.gui.getvar("ra2ceGUI", "run_name")

        # Network
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['network']['source'] = 'pickle'
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['network']['primary_file'] = Ra2ceGUI.loaded_roads

        # Origins and destinations
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['origins_destinations']['origins'] = [
            Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static', 'network', f"{Ra2ceGUI.loaded_roads.stem.split('_')[0]}.shp")]
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['origins_destinations']['destinations'] = [
            Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static', 'network', f"{Ra2ceGUI.loaded_roads.stem.split('_')[1]}.shp")]
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
            'origins_names'] = f"{Ra2ceGUI.loaded_roads.stem.split('_')[0]}"
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
            'destinations_names'] = f"{Ra2ceGUI.loaded_roads.stem.split('_')[1]}"
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
                'id_name_origin_destination'] = Ra2ceGUI.ra2ce_config['origins_destinations']['id_name_origin_destination']
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
            'origin_count'] = Ra2ceGUI.ra2ce_config['origins_destinations']['origin_count']

        # Hazard
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['hazard']['hazard_map'] = [Path(Ra2ceGUI.loaded_floodmap)]
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['hazard']['aggregate_wl'] = Ra2ceGUI.ra2ce_config['hazard']['zonal_stats']
        Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['hazard']['hazard_crs'] = Ra2ceGUI.ra2ce_config['hazard']['hazard_crs']

        # Update the Analyses ini configurations
        # Project
        Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['project']['name'] = Ra2ceGUI.gui.getvar("ra2ceGUI", "run_name")

        # Analyses
        for i in range(len(Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['indirect'])):
            if 'aggregate_wl' in Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i]:
                Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i]['aggregate_wl'] = Ra2ceGUI.ra2ce_config['hazard']['zonal_stats']
                Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i]['threshold'] = Ra2ceGUI.gui.getvar("ra2ceGUI", "threshold_road_disruption")

        # Update all GUI elements
        Ra2ceGUI.gui.setvar("ra2ceGUI", "valid_config", "Configuration updated")
        Ra2ceGUI.gui.update()
