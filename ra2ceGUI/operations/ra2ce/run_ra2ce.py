# -*- coding: utf-8 -*-
from ra2ceGUI import Ra2ceGUI
import geopandas as gpd


def analyzeFeedback(text):
    Ra2ceGUI.analyse_feedback = text
    Ra2ceGUI.gui.setvar("ra2ceGUI", "analyse_feedback", Ra2ceGUI.analyse_feedback)

    # Update all GUI elements
    Ra2ceGUI.gui.update()


def aggregate_results():
    #"D:\RA2CE\1_data\fullTest\output\multi_link_origin_closest_destination\fullTest_optimal_routes_with_hazard.gpkg"
    output_folder = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['output']
    Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['project']['name']
    routes_results_path = output_folder / r"multi_link_origin_closest_destination\fullTest_optimal_routes_with_hazard.gpkg"
    routes_results = gpd.read_file(routes_results_path)

    flooded_results = output_folder / "people_flooded.csv"


def runRA2CE():
    try:
        assert Ra2ceGUI.ra2ceHandler
    except AssertionError:
        analyzeFeedback("Validate configuration")
        return

    try:
        assert Ra2ceGUI.floodmap_overlay_feedback == "Overlay done"
    except AssertionError:
        analyzeFeedback("Overlay flood map")
        return

    try:
        Ra2ceGUI.ra2ceHandler.input_config.analysis_config.configure()
        Ra2ceGUI.ra2ceHandler.run_analysis()
        aggregate_results()
        analyzeFeedback("Analysis finished")
        print("RA2CE successfully ran.")
    except BaseException as e:
        print(e)
