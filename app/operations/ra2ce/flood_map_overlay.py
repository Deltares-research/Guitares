# -*- coding: utf-8 -*-
import rasterio
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from rasterstats import point_query
import osmnx

# from src.guitools.pyqt5.spinner import Spinner
from app.ra2ceGUI_base import Ra2ceGUI
from ra2ce.io.readers.graph_pickle_reader import GraphPickleReader
from ra2ce.io.writers.network_exporter_factory import NetworkExporterFactory


class FloodMapOverlay:
    def __init__(self):
        self.floodmap_extent = self.get_floodmap_extent()
        Ra2ceGUI.floodmap_extent = self.floodmap_extent
        self.overlay()

    @staticmethod
    def get_floodmap_extent():
        # Get the flood map extent
        dataset = rasterio.open(Ra2ceGUI.loaded_floodmap)
        return dataset.bounds

    @staticmethod
    def floodMapOverlayFeedback(text):
        Ra2ceGUI.floodmap_overlay_feedback = text
        Ra2ceGUI.gui.setvar("ra2ceGUI", "floodmap_overlay_feedback", Ra2ceGUI.floodmap_overlay_feedback)

        # Update all GUI elements
        Ra2ceGUI.gui.update()

    @staticmethod
    def hazard_overlay(point_gdf):
        from tqdm import tqdm  # somehow this only works when importing here and not at the top of the file

        # Do the hazard overlay
        tqdm.pandas(desc="Flood map overlay with " + Ra2ceGUI.loaded_floodmap.stem)
        flood_stats = point_gdf.geometry.progress_apply(
            lambda x: point_query(x, str(Ra2ceGUI.loaded_floodmap))
        )

        return flood_stats.apply(lambda x: x[0] if x[0] else 0)

    def floodmap_overlay_building_footprints(self):
        # Get the building footprints with the centroids / representative points within
        building_footprints_within_hazard_extent = gpd.read_feather(Ra2ceGUI.building_footprints_geoms)

        # Filter with the flood map bounding box
        xmin, ymin, xmax, ymax = self.floodmap_extent
        building_footprints_within_hazard_extent = building_footprints_within_hazard_extent.cx[xmin:xmax, ymin:ymax]

        # Update the GeoDataFrame with the flood map data
        building_footprints_within_hazard_extent["flooded_buildings"] = self.hazard_overlay(building_footprints_within_hazard_extent)

        # Calculate the number of people that are flooded
        building_footprints_within_hazard_extent["flooded_ppl"] = building_footprints_within_hazard_extent["flooded_buildings"] * building_footprints_within_hazard_extent["POP_BLDG"]

        # Summarize the number of people flooded and not flooded per village
        flooded_ppl = building_footprints_within_hazard_extent.groupby("VIL_NAME")[["flooded_buildings", "flooded_ppl"]].sum().reset_index()
        flooded_ppl["flooded_buildings"] = flooded_ppl["flooded_buildings"].astype(int)
        flooded_ppl["flooded_ppl"] = flooded_ppl["flooded_ppl"].astype(int)

        Ra2ceGUI.result = flooded_ppl
        Ra2ceGUI.result.to_csv(Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name, 'output', 'buildings_flooded.csv'),
                               index=False)

    def color_roads(self, graph_path):
        g = GraphPickleReader().read(graph_path)
        edges = osmnx.graph_to_gdfs(g, edges=True, nodes=False, node_geometry=False)
        edges = edges[[Ra2ceGUI.ra2ce_config["hazard"]["flood_col_name"], "geometry"]]
        edges[Ra2ceGUI.ra2ce_config["hazard"]["flood_col_name"]] = edges[Ra2ceGUI.ra2ce_config["hazard"]["flood_col_name"]].fillna(0)

        # Filter only the origins on the extent of the flood map
        xmin, ymin, xmax, ymax = self.floodmap_extent
        edges = edges.cx[xmin:xmax, ymin:ymax]

        edges = edges.to_json()

        layer_group = 'Road network'
        layer_name = 'roads_overlay'
        Ra2ceGUI.gui.elements['main_map']['widget_group'].add_line_geojson(edges,
                                                                           layer_name=layer_name,
                                                                           layer_group_name=layer_group,
                                                                           color_by=Ra2ceGUI.ra2ce_config["hazard"]["flood_col_name"])

    def overlay(self):
        # Ra2ceGUI.gui.elements["spinner"].start()

        path_od_hazard_graph = Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name, 'static', 'output_graph', 'origins_destinations_graph_hazard.p')
        if path_od_hazard_graph.is_file():
            print("A hazard overlay was already done previously. If you want to do a new hazard overlay, please create a new project.")
            self.color_roads(path_od_hazard_graph)
            Ra2ceGUI.floodmap_overlay_feedback = "Overlay done"
            self.floodMapOverlayFeedback(Ra2ceGUI.floodmap_overlay_feedback)
            # Ra2ceGUI.gui.elements["spinner"].stop()
            return

        try:
            assert Ra2ceGUI.ra2ceHandler
            Ra2ceGUI.floodmap_overlay_feedback = "First validate configuration"
            self.floodMapOverlayFeedback(Ra2ceGUI.floodmap_overlay_feedback)
        except AssertionError:
            # Ra2ceGUI.gui.elements["spinner"].stop()
            return

        # Clip the origins to the extent of the hazard map
        clip_origins(self.floodmap_extent)

        if Ra2ceGUI.floodmap_overlay_feedback == "No origins in extent":
            self.floodMapOverlayFeedback(Ra2ceGUI.floodmap_overlay_feedback)
            # Ra2ceGUI.gui.elements["spinner"].stop()
            return

        try:
            Ra2ceGUI.ra2ceHandler.input_config.network_config.configure_hazard()
            self.floodmap_overlay_building_footprints()
            self.color_roads(path_od_hazard_graph)
            self.floodMapOverlayFeedback("Overlay done")
        except BaseException as e:
            print(e)

        # Ra2ceGUI.gui.elements["spinner"].stop()


def clip_origins(clip_extent: rasterio.coords.BoundingBox):
    # Get the origin and destination names
    origin_name_ = Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
                    'origins_names']
    destination_name_ = Ra2ceGUI.ra2ceHandler.input_config.network_config.config_data['origins_destinations'][
                    'destinations_names']

    # Get the paths of the OD graph and table
    od_graph_path = Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                       'static',
                                                       'output_graph',
                                                       'origins_destinations_graph.p')
    od_table_path = Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                       'static',
                                                       'output_graph',
                                                       'origin_destination_table.feather')

    # Convert the Rasterio bounding box to a Polygon object for removing origin nodes outside of the hazard extent
    clip_extent_box = box(*clip_extent, ccw=True)

    # Load the graph, remove the origin nodes outside of the extent and
    od_graph = GraphPickleReader().read(od_graph_path)
    od_graph = remove_nodes_within_extent(od_graph, clip_extent_box, origin_name_, destination_name_)

    if od_graph:
        NetworkExporterFactory().export(od_graph, 'origins_destinations_graph',
                                        od_graph_path.parent,
                                        'pickle')
    else:
        Ra2ceGUI.floodmap_overlay_feedback = "No origins in extent"

    # Load the OD table and split it into origins and destinations
    od_table_ = gpd.read_feather(od_table_path)
    od_table_ = filter_od_table_within_extent(od_table_, clip_extent)

    if not od_table_.empty:
        od_table_.to_feather(od_table_path, index=False)
    else:
        Ra2ceGUI.floodmap_overlay_feedback = "No origins in extent"


def remove_nodes_within_extent(g, extent, origin_name, destination_name):
    nodes_remove = [n for n in g.nodes.data() if 'od_id' in n[-1]
                    and not n[-1]['geometry'].within(extent)
                    and origin_name in n[-1]['od_id']
                    ]

    list_origins_only = [n[0] for n in nodes_remove if destination_name not in n[-1]['od_id']]
    list_destinations_and_origins = [n[0] for n in nodes_remove if destination_name in n[-1]['od_id']]

    to_remove = len(list_origins_only + list_destinations_and_origins)

    if to_remove > 0:
        # Remove the attributes for origin nodes
        for node in list_origins_only:
            del g.nodes[node]["od_id"]

        for node in list_destinations_and_origins:
            # Delete the origin name from the "od_id" attribute of the nodes of which the origin is outside of the extent.
            od_id = g.nodes[node]["od_id"]
            g.nodes[node]["od_id"] = ",".join([od for od in od_id.split(",") if destination_name not in od])

        return g
    else:
        return None


def filter_od_table_within_extent(od_table, extent):
    od_table_destinations = od_table.loc[od_table['d_id'].notnull()]
    od_table_origins = od_table.loc[od_table['o_id'].notnull()]

    # Filter only the origins on the extent of the flood map
    xmin, ymin, xmax, ymax = extent
    od_table_origins = od_table_origins.cx[xmin:xmax, ymin:ymax]

    if od_table_origins.empty:
        return gpd.GeoDataFrame()

    # Create again one table from the origins and destinations
    od_table = gpd.GeoDataFrame(pd.concat([od_table_origins, od_table_destinations], ignore_index=True))

    return od_table
