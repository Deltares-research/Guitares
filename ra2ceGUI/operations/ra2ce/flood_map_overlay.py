# -*- coding: utf-8 -*-
import rasterio
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from rasterstats import point_query
import networkx as nx

from ra2ceGUI import Ra2ceGUI
from ra2ce.io.readers.graph_pickle_reader import GraphPickleReader
from ra2ce.io.writers.network_exporter_factory import NetworkExporterFactory


class FloodMapOverlay:
    def __init__(self):
        self.floodmap_extent = self.get_floodmap_extent()
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
        building_footprints_within_hazard_extent = gpd.read_file(Ra2ceGUI.building_footprints, bbox=self.floodmap_extent)

        # Get the centroids / representative points within the building footprints
        building_footprints_within_hazard_extent.geometry = building_footprints_within_hazard_extent.representative_point()

        # Update the GeoDataFrame with the flood map data
        building_footprints_within_hazard_extent["flooded"] = self.hazard_overlay(building_footprints_within_hazard_extent)

        # Summarize the number of people flooded and not flooded per village
        flooded_ppl = building_footprints_within_hazard_extent.loc[building_footprints_within_hazard_extent["flooded"] == 1].groupby("VIL_NAME")["flooded"].size().reset_index()
        non_flooded_ppl = building_footprints_within_hazard_extent.loc[building_footprints_within_hazard_extent["flooded"] == 0].groupby("VIL_NAME")["flooded"].size().reset_index()
        non_flooded_ppl.rename(columns={"flooded": "not flooded"}, inplace=True)

        Ra2ceGUI.result = pd.merge(flooded_ppl, non_flooded_ppl, how='outer', on="VIL_NAME")
        Ra2ceGUI.result.to_csv(Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name, 'output', 'people_flooded.csv'))


    def overlay(self):
        path_od_hazard_graph = Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name, 'static', 'output_graph', 'origins_destinations_graph_hazard.p')
        if path_od_hazard_graph.is_file():
            print("A hazard overlay was already done previously. Please create a new project.")
            # self.floodMapOverlayFeedback("Create a new project")
            # return

        try:
            assert Ra2ceGUI.ra2ceHandler
            self.floodMapOverlayFeedback("First validate configuration")
        except AssertionError:
            return

        # Clip the origins to the extent of the hazard map
        clip_origins(self.floodmap_extent)

        try:
            Ra2ceGUI.ra2ceHandler.input_config.network_config.configure_hazard()
            self.floodmap_overlay_building_footprints()
            self.floodMapOverlayFeedback("Overlay done")
        except BaseException as e:
            print(e)


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
    NetworkExporterFactory().export(od_graph, 'origins_destinations_graph',
                                    od_graph_path.parent,
                                    'pickle')

    # Load the OD table and split it into origins and destinations
    od_table_ = gpd.read_feather(od_table_path)
    od_table_ = filter_od_table_within_extent(od_table_, clip_extent)
    od_table_.to_feather(od_table_path, index=False)


def remove_nodes_within_extent(g, extent, origin_name, destination_name):
    nodes_remove = [n for n in g.nodes.data() if 'od_id' in n[-1]
                    and not n[-1]['geometry'].within(extent)
                    and origin_name in n[-1]['od_id']
                    ]

    list_origins_only = [n[0] for n in nodes_remove if destination_name not in n[-1]['od_id']]
    list_destinations_and_origins = [n[0] for n in nodes_remove if destination_name in n[-1]['od_id']]

    to_remove = len(list_origins_only + list_destinations_and_origins)

    if to_remove > 0:
        # Remove the flooded destination nodes
        g.remove_nodes_from(list_origins_only)

        for node in list_destinations_and_origins:
            # Delete the destination name from the "od_id" attribute of the nodes of which the destination is
            # flooded.
            od_id = g.nodes[node]["od_id"]
            g.nodes[node]["od_id"] = ",".join([od for od in od_id.split(",") if destination_name not in od])

    return g


def filter_od_table_within_extent(od_table, extent):
    od_table_destinations = od_table.loc[od_table['d_id'].notnull()]
    od_table_origins = od_table.loc[od_table['o_id'].notnull()]

    # Filter only the origins on the extent of the flood map
    xmin, ymin, xmax, ymax = extent
    od_table_origins = od_table_origins.cx[xmin:xmax, ymin:ymax]

    # Create again one table from the origins and destinations
    od_table = gpd.GeoDataFrame(pd.concat([od_table_origins, od_table_destinations], ignore_index=True))

    return od_table
