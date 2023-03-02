# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.
#
# This tool is developed for demonstration purposes only.

from app.ra2ceGUI_base import Ra2ceGUI
from src.guitools.pyqt5.io import openFileNameDialog
from ra2ce.io.readers.graph_pickle_reader import GraphPickleReader

import logging
import numpy as np
import osmnx
from pathlib import Path


def roadModificationFeedback(text):
    Ra2ceGUI.modification_feedback = text
    Ra2ceGUI.gui.setvar("ra2ceGUI", "modification_feedback", Ra2ceGUI.modification_feedback)

    # Update all GUI elements
    Ra2ceGUI.gui.update()


def color_roads():
    edges = osmnx.graph_to_gdfs(Ra2ceGUI.graph, edges=True, nodes=False, node_geometry=False)
    edges = edges[[Ra2ceGUI.ra2ce_config["hazard"]["flood_col_name"], "geometry"]]
    edges[Ra2ceGUI.ra2ce_config["hazard"]["flood_col_name"]] = edges[Ra2ceGUI.ra2ce_config["hazard"]["flood_col_name"]].fillna(0)

    # Filter only the origins on the extent of the flood map
    xmin, ymin, xmax, ymax = Ra2ceGUI.floodmap_extent
    edges = edges.cx[xmin:xmax, ymin:ymax]

    edges = edges.to_json()

    Ra2ceGUI.remove_roads('selected_road')

    # Remove the previous roads
    Ra2ceGUI.gui.elements['main_map']['widget_group'].remove_layer('roads')

    layer_name = 'roads_overlay'
    Ra2ceGUI.gui.elements['main_map']['widget_group'].add_line_geojson(edges,
                                                                       layer_name=layer_name,
                                                                       color_by=Ra2ceGUI.ra2ce_config["hazard"]["flood_col_name"])


def modifyFloodDepth():
    Ra2ceGUI.edited_flood_depth = Ra2ceGUI.gui.getvar("ra2ceGUI", "edited_flood_depth")
    logging.info(f'Flood depth input: {Ra2ceGUI.edited_flood_depth}')

    Ra2ceGUI.graph.edges[Ra2ceGUI.closest_u_v_k[0], Ra2ceGUI.closest_u_v_k[1], Ra2ceGUI.closest_u_v_k[2]][Ra2ceGUI.ra2ce_config["hazard"]["flood_col_name"]] = Ra2ceGUI.edited_flood_depth

    # TODO do this always immediately or only after someone is done editing?
    from ra2ce.io.writers.multi_graph_network_exporter import MultiGraphNetworkExporter

    exporter = MultiGraphNetworkExporter(basename='origins_destinations_graph_hazard', export_types=["pickle"])
    exporter.export_to_pickle(
        Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data["static"].joinpath("output_graph"),
        Ra2ceGUI.graph)

    color_roads()

    # Remove the marker from the map after the road has been edited

    roadModificationFeedback("Road data updated")


def selectRoad():
    Ra2ceGUI.remove_roads('selected_road')

    coords = Ra2ceGUI.gui.getvar("ra2ceGUI", "coords_clicked")

    try:
        assert coords
    except AssertionError:
        roadModificationFeedback("Select a road")
        return

    try:
        assert Ra2ceGUI.ra2ceHandler
    except AssertionError:
        roadModificationFeedback("Overlay flood map first")
        return

    path_od_hazard_graph = Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name, 'static', 'output_graph', 'origins_destinations_graph_hazard.p')
    if path_od_hazard_graph.is_file():
        if not Ra2ceGUI.graph:
            Ra2ceGUI.graph = GraphPickleReader().read(path_od_hazard_graph)

        # create dictionary of the roads geometries
        edge_list = [e for e in Ra2ceGUI.graph.edges.data(keys=True) if "geometry" in e[-1]]
        inverse_vertices_dict = {}
        for i, line in enumerate(edge_list):
            inverse_vertices_dict.update(
                {p: (line[0], line[1], line[2]) for p in set(list(line[-1]["geometry"].coords))})

        # create list of all points to search in
        all_vertices = np.array([p for p in list(inverse_vertices_dict.keys())])

        def closest_node(node, nodes):
            deltas = nodes - node
            dist_2 = np.einsum('ij,ij->i', deltas, deltas)
            return nodes[np.argmin(dist_2)]

        closest_node_on_road = closest_node(np.array((coords['lng'], coords['lat'])), all_vertices)
        closest_u_v_k = inverse_vertices_dict[(closest_node_on_road[0], closest_node_on_road[1])]
        Ra2ceGUI.closest_u_v_k = closest_u_v_k

        # Highlight the selected road in yellow in the interface
        to_highlight = Ra2ceGUI.graph.edges[closest_u_v_k[0], closest_u_v_k[1], closest_u_v_k[2]]["geometry"]
        Ra2ceGUI.highlight_road(to_highlight, 'selected_road')

        roadModificationFeedback("Road selected")


def showRoads():
    Ra2ceGUI.gui.process('Loading roads... Please wait.')

    Ra2ceGUI.show_roads()

    Ra2ceGUI.gui.process('Ready.')


def showFloodmap():
    Ra2ceGUI.gui.process('Loading flood map... Please wait.')

    if Ra2ceGUI.previous_floodmap:
        Ra2ceGUI.gui.map_widget["main_map"].remove_layer("flood_map")
        Ra2ceGUI.gui.setvar("ra2ceGUI", "valid_config", "Not yet configured")

    try:
        Ra2ceGUI.update_flood_map()

    except:
        Ra2ceGUI.gui.setvar("ra2ceGUI", "loaded_floodmap", "Cannot load flood map in GUI")

    Ra2ceGUI.previous_floodmap = Ra2ceGUI.loaded_floodmap.name

    Ra2ceGUI.gui.process('Ready.')

    # Update all GUI elements
    Ra2ceGUI.gui.update()


def selectFloodmap():
    _loaded_floodmap = openFileNameDialog(Ra2ceGUI.current_project.joinpath('static', 'hazard'),
                                          fileTypes=["GeoTIFF files (*.tif)"])

    if _loaded_floodmap:
        Ra2ceGUI.loaded_floodmap = Path(_loaded_floodmap)
        Ra2ceGUI.gui.setvar("ra2ceGUI", "loaded_floodmap", Path(Ra2ceGUI.loaded_floodmap).name)

        # Update all GUI elements
        Ra2ceGUI.gui.update()
