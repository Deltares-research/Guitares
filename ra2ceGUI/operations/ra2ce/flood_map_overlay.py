# -*- coding: utf-8 -*-
import rasterio
import geopandas as gpd

from ra2ceGUI import Ra2ceGUI


def floodMapOverlayFeedback(text):
    Ra2ceGUI.floodmap_overlay_feedback = text
    Ra2ceGUI.gui.setvar("ra2ceGUI", "floodmap_overlay_feedback", Ra2ceGUI.floodmap_overlay_feedback)

    # Update all GUI elements
    Ra2ceGUI.gui.update()


def floodmap_overlay_building_footprints():
    # Get the flood map extent
    dataset = rasterio.open(Ra2ceGUI.loaded_floodmap)
    floodmap_extent = dataset.bounds

    building_footprints_within_hazard_extent = gpd.read_file(Ra2ceGUI.building_footprints, bbox=floodmap_extent)


def floodMapOverlay():
    path_od_hazard_graph = Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name, 'static', 'output_graph', 'origins_destinations_graph_hazard.p')
    if path_od_hazard_graph.is_file():
        print("A hazard overlay was already done previously. Please create a new project.")
        floodMapOverlayFeedback("Create a new project")
        return

    try:
        assert Ra2ceGUI.ra2ceHandler
        floodMapOverlayFeedback("First validate configuration")
    except AssertionError:
        return

    try:
        Ra2ceGUI.ra2ceHandler.input_config.network_config.configure_hazard()
        floodmap_overlay_building_footprints()
        floodMapOverlayFeedback("Overlay done")
    except BaseException as e:
        print(e)
