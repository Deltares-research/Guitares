from ra2ceGUI import Ra2ceGUI
from guitools.pyqt5.io import openFileNameDialog

from pathlib import Path


def selectRoad():
    coords = Ra2ceGUI.gui.getvar("ra2ceGUI", "coords_clicked")

    # Remove the marker from the map after the road has been selected

    Ra2ceGUI.edited_flood_depth = Ra2ceGUI.gui.getvar("ra2ceGUI", "edited_flood_depth")
    print(f'Flood depth input: {Ra2ceGUI.edited_flood_depth}')

    Ra2ceGUI.ra2ceHandler.configure()

    get_graphs = ['base_graph_hazard']
    Ra2ceGUI.graph = Ra2ceGUI.ra2ceHandler.input_config.network_config.graphs[get_graphs[0]]

    # create dictionary of the roads geometries
    edge_list = [e for e in Ra2ceGUI.graph.edges.data(keys=True) if "geometry" in e[-1]]
    for i, line in enumerate(edge_list):
        inverse_vertices_dict = {p: (line[0], line[1], line[2]) for p in set(list(line[-1]["geometry"].coords))}

    import numpy as np
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
    # id_name = Ra2ceGUI.ra2ce_config["network"]["id_name"]
    # Ra2ceGUI.graph.edges[closest_u_v_k[0], closest_u_v_k[1], closest_u_v_k[2]][id_name]

    # TODO do this always immediately or only after someone is done editing?
    from ra2ce.io.writers.multi_graph_network_exporter import MultiGraphNetworkExporter
    exporter = MultiGraphNetworkExporter(basename=get_graphs[0], export_types=["pickle"])
    exporter.export_to_pickle(Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data["static"].joinpath("output_graph"),
                              Ra2ceGUI.graph)


def showRoads():
    Ra2ceGUI.show_roads()


def openRoads():
    # Get the selected path
    Ra2ceGUI.loaded_roads = Ra2ceGUI.current_project.joinpath('static',
                                                              'network',
                                                              f"{Ra2ceGUI.gui.getvar('ra2ceGUI', 'loaded_roads')}.p")

    if Ra2ceGUI.loaded_roads:
        # Update the text to show underneath the button
        Ra2ceGUI.gui.setvar("ra2ceGUI", "loaded_roads_string", Ra2ceGUI.map_roads_values_strings[Ra2ceGUI.gui.getvar("ra2ceGUI", "loaded_roads")])

        # Update all GUI elements
        Ra2ceGUI.gui.update()


def selectFloodmap():
    _loaded_floodmap = openFileNameDialog(Ra2ceGUI.current_project.joinpath('static', 'hazard'),
                                          fileTypes=["GeoTIFF files (*.tif)"])
    if _loaded_floodmap:
        Ra2ceGUI.loaded_floodmap = Path(_loaded_floodmap)
        Ra2ceGUI.update_flood_map()
        Ra2ceGUI.gui.setvar("ra2ceGUI", "loaded_floodmap", Path(Ra2ceGUI.loaded_floodmap).name)

        # Update all GUI elements
        Ra2ceGUI.gui.update()
