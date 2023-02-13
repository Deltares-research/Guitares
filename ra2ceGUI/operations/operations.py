from ra2ceGUI import Ra2ceGUI
from src.guitools.pyqt5.io import openFileNameDialog
from ra2ce.io.readers.graph_pickle_reader import GraphPickleReader

import numpy as np
import osmnx
from pathlib import Path


def roadModificationFeedback(text):
    Ra2ceGUI.modification_feedback = text
    Ra2ceGUI.gui.setvar("ra2ceGUI", "modification_feedback", Ra2ceGUI.modification_feedback)

    # Update all GUI elements
    Ra2ceGUI.gui.update()


def selectRoad():
    coords = Ra2ceGUI.gui.getvar("ra2ceGUI", "coords_clicked")

    # Remove the marker from the map after the road has been selected

    Ra2ceGUI.edited_flood_depth = Ra2ceGUI.gui.getvar("ra2ceGUI", "edited_flood_depth")
    print(f'Flood depth input: {Ra2ceGUI.edited_flood_depth}')

    try:
        assert Ra2ceGUI.ra2ceHandler
    except AssertionError:
        roadModificationFeedback("Overlay flood map first")
        return

    path_od_hazard_graph = Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name, 'static', 'output_graph', 'origins_destinations_graph_hazard.p')
    if path_od_hazard_graph.is_file():
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
        Ra2ceGUI.graph.edges[closest_u_v_k[0], closest_u_v_k[1], closest_u_v_k[2]]['F_EV1_ma'] = Ra2ceGUI.edited_flood_depth

        # Highlight the selected road in yellow in the interface
        to_highlight = Ra2ceGUI.graph.edges[closest_u_v_k[0], closest_u_v_k[1], closest_u_v_k[2]]["geometry"]
        Ra2ceGUI.highlight_road(to_highlight, 'Road network', 'selected_road')

        # TODO do this always immediately or only after someone is done editing?
        from ra2ce.io.writers.multi_graph_network_exporter import MultiGraphNetworkExporter
        exporter = MultiGraphNetworkExporter(basename='origins_destinations_graph_hazard', export_types=["pickle"])
        exporter.export_to_pickle(Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data["static"].joinpath("output_graph"),
                                  Ra2ceGUI.graph)

        edges = osmnx.graph_to_gdfs(Ra2ceGUI.graph, edges=True)
        edges = edges.to_json()

        layer_group = 'Road network'
        layer_name = 'roads_overlay'
        Ra2ceGUI.gui.elements['main_map']['widget_group'].add_line_geojson(edges,
                                                                           layer_name=layer_name,
                                                                           layer_group_name=layer_group,
                                                                           color_by=True)


def showRoads():
    Ra2ceGUI.gui.elements["spinner"].start()

    Ra2ceGUI.show_roads()

    Ra2ceGUI.gui.elements["spinner"].stop()


def selectFloodmap():
    _loaded_floodmap = openFileNameDialog(Ra2ceGUI.current_project.joinpath('static', 'hazard'),
                                          fileTypes=["GeoTIFF files (*.tif)"])

    if Ra2ceGUI.previous_floodmap:
        Ra2ceGUI.gui.map_widget["main_map"].remove_layer("flood_map_layer_group", Ra2ceGUI.previous_floodmap)

    if _loaded_floodmap:
        Ra2ceGUI.gui.elements["spinner"].start()

        Ra2ceGUI.loaded_floodmap = Path(_loaded_floodmap)
        Ra2ceGUI.update_flood_map()
        Ra2ceGUI.previous_floodmap = Ra2ceGUI.loaded_floodmap.name
        Ra2ceGUI.gui.setvar("ra2ceGUI", "loaded_floodmap", Path(Ra2ceGUI.loaded_floodmap).name)

        # Update all GUI elements
        Ra2ceGUI.gui.update()
        Ra2ceGUI.gui.elements["spinner"].stop()
