# -*- coding: utf-8 -*-
import rasterio
import pandas as pd
import geopandas as gpd
from rasterstats import point_query

from ra2ceGUI import Ra2ceGUI


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

        Ra2ceGUI.result = pd.merge(flooded_ppl, non_flooded_ppl, how='outer', on="VIL_NAME")

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
        clip_origins()

        try:
            # Ra2ceGUI.ra2ceHandler.input_config.network_config.configure_hazard()
            self.floodmap_overlay_building_footprints()
            self.floodMapOverlayFeedback("Overlay done")
        except BaseException as e:
            print(e)


def clip_origins():
    Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                       'static',
                                                       'output_graph',
                                                       'origins_destinations_graph.p')

    Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name,
                                                       'static',
                                                       'output_graph',
                                                       'origin_destination_table.feather')