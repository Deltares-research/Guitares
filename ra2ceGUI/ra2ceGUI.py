# -*- coding: utf-8 -*-
import os, sys
from pathlib import Path

from src.guitools.gui import GUI
from ra2ce.io.readers.ini_file_reader import IniFileReader


class Ra2ceGUI:
    def __init__(self):
        # Determine if application is a script file or frozen exe and set the main path
        if getattr(sys, 'frozen', False):
            self.main_path = Path(sys.executable).resolve().parent  # When running from the executable
        elif __file__:
            self.main_path = Path(__file__).resolve().parent  # When running from script

        # Read the additional ini file (for RA2CE) and convert the paths to pathlib Paths
        self.ra2ce_ini = Path(self.main_path).joinpath('ra2ce.ini')
        self.ra2ce_config = IniFileReader().read(self.ra2ce_ini)
        self.ra2ce_config['database']['path'] = Path(self.ra2ce_config['database']['path'])
        self.ra2ce_config['base_data']['path'] = Path(self.ra2ce_config['base_data']['path'])

        server_path = os.path.join(self.main_path, "server")
        self.server_path = server_path

        # Get the base data paths
        self.base_graph = self.ra2ce_config['base_data']['path'] / 'network' / 'base_graph.p'
        self.base_network = self.ra2ce_config['base_data']['path'] / 'network' / 'base_network.feather'
        self.origins_destinations_graph = self.ra2ce_config['base_data']['path'] / 'network' / 'origins_destinations_graph.p'
        self.origin_destination_table = self.ra2ce_config['base_data']['path'] / 'network' / 'origin_destination_table.feather'
        self.validate_base_data()

        # Initialize a RA2CE handler
        self.ra2ceHandler = None

        self.gui = GUI(self,
                       framework="pyqt5",
                       splash_file="ra2ceGUI.jpg",
                       config_file="ra2ceGUI.yml",
                       stylesheet="Combinear.qss",
                       config_path=self.main_path,
                       server_path=server_path,
                       server_port=3000)

    def initialize(self):
        # Define variables
        self.loaded_floodmap = "Not yet selected"
        self.valid_config = "Not yet configured"
        self.coords_clicked = None
        self.run_name = "Choose a name"
        self.edited_flood_depth = 0.
        self.current_project = Path()

        # Define GUI variables
        self.gui.setvar("ra2ceGUI", "run_name", self.run_name)
        self.gui.setvar("ra2ceGUI", "loaded_floodmap", self.loaded_floodmap)
        self.gui.setvar("ra2ceGUI", "threshold_road_disruption", 0.)  # 0 as default value?
        self.gui.setvar("ra2ceGUI", "valid_config", self.valid_config)
        self.gui.setvar("ra2ceGUI", "coords_clicked", self.coords_clicked)
        self.gui.setvar("ra2ceGUI", "edited_flood_depth", self.edited_flood_depth)

    def validate_base_data(self):
        required_base_data = [self.base_graph, self.base_network,
                              self.origins_destinations_graph, self.origin_destination_table]
        for base_data in required_base_data:
            if not base_data.is_file():
                print(f"Warning: {str(base_data)} cannot be found!")

    def valid_input(self):
        _original_value = "Choose a name"
        if isinstance(self.loaded_floodmap, str):
            self.gui.setvar("ra2ceGUI", "valid_config", "Select a flood map")
            self.gui.update()
            return False

        if self.loaded_floodmap.is_file() and self.gui.getvar("ra2ceGUI",
                                                              "run_name") != _original_value:
            return True
        else:
            if not self.loaded_floodmap.is_file() and self.gui.getvar("ra2ceGUI",
                                                                      "run_name") != _original_value:
                self.gui.setvar("ra2ceGUI", "valid_config", "Select a flood map")
            elif self.loaded_floodmap.is_file() and self.gui.getvar("ra2ceGUI",
                                                                    "run_name") == _original_value:
                self.gui.setvar("ra2ceGUI", "valid_config", "Provide a run name")
            elif not self.loaded_floodmap.is_file() and self.gui.getvar("ra2ceGUI",
                                                                        "run_name") == _original_value:
                self.gui.setvar("ra2ceGUI", "valid_config", "Provide a run name")
            self.gui.update()
            return False

    def show_roads(self):
        # Find the layer group
        layer_group = 'Road network'
        layer_name = 'roads'
        self.gui.elements['main_map']['widget_group'].add_layer_group(layer_group)

        # Add the road network to the map
        path_roads = self.ra2ce_config['base_data']['path'].joinpath('network', self.ra2ce_config['network']['geojson'])
        self.gui.elements['main_map']['widget_group'].add_line_geojson(path_roads,
                                                                       'red',
                                                                       layer_name,
                                                                       layer_group)

    def highlight_road(self, roads, layer_name, layer_group):
        self.gui.elements['main_map']['widget_group'].add_line_geojson(roads,
                                                                       'yellow',
                                                                       layer_name,
                                                                       layer_group)

    def update_flood_map(self):
        layer_name = Path(self.loaded_floodmap).name
        layer_group_name = "flood_map_layer_group"

        # Add layer group (this only does something when there is no layer group with layer_group_name)
        self.gui.map_widget["main_map"].add_layer_group(layer_group_name)

        # Remove old layer from layer group
        self.gui.map_widget["main_map"].remove_layer(layer_name, layer_group_name)

        # And now add the new image layer to the layer group
        self.gui.map_widget["main_map"].add_image_layer(Ra2ceGUI.loaded_floodmap,
                                                            layer_name=layer_name,
                                                            layer_group_name=layer_group_name,
                                                            legend_title="Depth (m)",
                                                            colormap="jet",
                                                            cmin=0.2,
                                                            cmax=2.0,
                                                            cstep=0.2,
                                                            decimals=1)

    def update_network_config(self):
        # Update the Network ini configurations
        # Project
        self.ra2ceHandler.input_config.network_config.config_data['project']['name'] = self.gui.getvar("ra2ceGUI",
                                                                                                       "run_name")

        # Network
        self.ra2ceHandler.input_config.network_config.config_data['network']['source'] = 'pickle'
        self.ra2ceHandler.input_config.network_config.config_data['network']['primary_file'] = self.ra2ce_config['network']['shp']
        self.ra2ceHandler.input_config.network_config.config_data['network']['file_id'] = self.ra2ce_config['network']['id_name']

        # Origins and destinations
        self.ra2ceHandler.input_config.network_config.config_data['origins_destinations']['origins'] = [
            Path(self.ra2ce_config['base_data']['path']).joinpath('network',
                                                                  self.ra2ce_config['origins_destinations']['origins'])]
        self.ra2ceHandler.input_config.network_config.config_data['origins_destinations']['destinations'] = [
            Path(self.ra2ce_config['base_data']['path']).joinpath('network',
                                                                  self.ra2ce_config['origins_destinations']['destinations'])]
        self.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
            'origins_names'] = self.ra2ce_config['origins_destinations']['origins_names']
        self.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
            'destinations_names'] = self.ra2ce_config['origins_destinations']['destinations_names']
        self.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
            'id_name_origin_destination'] = self.ra2ce_config['origins_destinations']['id_name_origin_destination']
        self.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
            'origin_count'] = self.ra2ce_config['origins_destinations']['origin_count']
        self.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
            'categories'] = self.ra2ce_config['origins_destinations']['categories']

        # Hazard
        self.ra2ceHandler.input_config.network_config.config_data['hazard']['hazard_map'] = [
            self.loaded_floodmap]
        self.ra2ceHandler.input_config.network_config.config_data['hazard']['aggregate_wl'] = \
            self.ra2ce_config['hazard']['zonal_stats']
        self.ra2ceHandler.input_config.network_config.config_data['hazard']['hazard_crs'] = \
            self.ra2ce_config['hazard']['hazard_crs']

    def update_analyses_config(self):
        # Update the Analyses ini configurations
        # Project
        self.ra2ceHandler.input_config.analysis_config.config_data['project']['name'] = self.gui.getvar("ra2ceGUI",
                                                                                                        "run_name")

        # Analyses
        for i in range(len(self.ra2ceHandler.input_config.analysis_config.config_data['indirect'])):
            if 'aggregate_wl' in self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i]:
                self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i]['aggregate_wl'] = \
                    self.ra2ce_config['hazard']['zonal_stats']
            if 'threshold' in self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i]:
                self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i][
                    'threshold'] = self.gui.getvar("ra2ceGUI", "threshold_road_disruption")
            if 'name' in self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i]:
                self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i][
                    'name'] = self.gui.getvar("ra2ceGUI", "run_name")
            if 'weighing' in self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i]:
                self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i][
                    'weighing'] = self.ra2ce_config['analyses']['weighing']
            if 'save_shp' in self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i]:
                self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i][
                    'weighing'] = self.ra2ce_config['analyses']['save_shp']
            if 'save_csv' in self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i]:
                self.ra2ceHandler.input_config.analysis_config.config_data['indirect'][i][
                    'weighing'] = self.ra2ce_config['analyses']['save_csv']


Ra2ceGUI = Ra2ceGUI()
