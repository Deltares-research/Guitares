# -*- coding: utf-8 -*-
from src.guitools.pyqt5.worker import Worker
from app.ra2ceGUI_base import Ra2ceGUI

import logging
from PyQt5.QtCore import QThreadPool
import geopandas as gpd
import pandas as pd

rename_cols = {'EV1_ma_AD1': 'Health facility access',
               'EV1_ma_AD2': 'HSA Warehouse access',
               'EV1_ma_AD3': 'Market access',
               'VIL_NAME': 'Village',
               'flooded_buildings': '# of flooded buildings',
               'flooded_ppl': '# of flooded people',
               'DISTRICT': 'District',
               'Municipal': 'Municipality',
               'Ward_no': 'Ward Number'
               }
save_cols = ['Village', 'District', 'Municipality',
             'Ward Number', '# of flooded people', '# of flooded buildings',
             'HSA Warehouse access', 'Market access', 'Health facility access',
             'Distance [km] to HSA Warehouse', 'Distance [km] to Market',
             'Distance [km] to Health facility', ]


def analyzeFeedback(text):
    Ra2ceGUI.analyse_feedback = text
    Ra2ceGUI.gui.setvar("ra2ceGUI", "analyse_feedback", Ra2ceGUI.analyse_feedback)

    # Update all GUI elements
    Ra2ceGUI.gui.update()


def get_col_widths(dataframe):
    """Set col width 'autofit' style
    Adjusted from https://stackoverflow.com/questions/29463274/simulate-autofit-column-in-xslxwriter
    """
    # Return the max of the lengths of column name and its values for each column, left to right
    if isinstance(dataframe.columns, pd.MultiIndex):
        # First we find the maximum length of the index column
        idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
        tot = [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col[0])] + [len(col[1])]) for col in
                     dataframe.columns]
    else:
        tot = [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

    return [t + 2 for t in tot]


def write_to_sheet_table(xlsx_writer, data, name, indexing=False):
    # Write each dataframe to a different worksheet.
    data.to_excel(xlsx_writer, sheet_name=name, index=indexing)

    # Get the xlsxwriter workbook and worksheet objects.
    worksheet = xlsx_writer.sheets[name]

    # Get the dimensions of the dataframe.
    (max_row, max_col) = data.shape

    # Create a list of column headers, to use in add_table().
    column_settings = [{'header': column} for column in data.columns]

    # Add the Excel table structure. Pandas will add the data.
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})

    # Make the columns wider for clarity.
    for i, width in enumerate(get_col_widths(data)):
        worksheet.set_column(i, i, width)


def aggregate_results():
    # Get the paths
    output_folder = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['output']
    project_name = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['project']['name']
    origins_path = output_folder / "multi_link_origin_closest_destination/{}_origins.gpkg".format(project_name)
    flooded_results_path = output_folder / "buildings_flooded.csv"
    route_paths_path = output_folder / "multi_link_origin_closest_destination/{}_optimal_routes_with_hazard.gpkg".format(project_name)

    # Read the results data
    origins = gpd.read_file(origins_path)
    flooded_results = pd.read_csv(flooded_results_path)
    route_paths = gpd.read_file(route_paths_path)
    id_to_vilname = pd.read_feather(Ra2ceGUI.village_ids)

    # Transform the optimal routes and origins geodataframes to something that can be added to the summary results
    route_paths['FID'] = route_paths['origin'].apply(lambda x: x.replace("village_",  ""))
    route_paths['FID'] = route_paths['FID'].apply(lambda x: x.split(","))
    route_paths['Distance [km]'] = route_paths['length'] / 1000
    route_paths = route_paths[['FID', 'category', 'Distance [km]']]
    route_paths = route_paths.explode(['FID'], ignore_index=True)
    route_paths = pd.pivot(route_paths, index=['FID'], columns=['category'], values=['Distance [km]'])
    route_paths = route_paths.droplevel(level=0, axis=1).reset_index()
    route_paths[['HSA Warehouse', 'Health facility', 'Market']] = route_paths[['HSA Warehouse', 'Health facility', 'Market']].round(1)
    route_paths.rename(columns={'HSA Warehouse': 'Distance [km] to HSA Warehouse',
                                'Health facility': 'Distance [km] to Health facility',
                                'Market': 'Distance [km] to Market'},
                       inplace=True)
    route_paths = route_paths.loc[route_paths['FID'].apply(lambda x: 'POI' not in x)]
    route_paths['FID'] = route_paths['FID'].astype(int)

    origins['FID'] = origins['o_id'].apply(lambda x: int(x.split("_")[-1]))
    origins = pd.merge(origins, id_to_vilname[['FID', 'VIL_NAME', 'DISTRICT', 'Municipal', 'Ward_no']], on="FID")
    if 'POI' in origins.columns:
        del origins["POI"]

    # TODO: fix issue with the villages with the same names
    total_results = pd.merge(flooded_results, origins, on="VIL_NAME")
    total_results = pd.merge(total_results, route_paths, on="FID")
    total_results.rename(columns=rename_cols, inplace=True)
    for d in ['o_id', 'cnt', 'geometry', 'FID']:
        if d in total_results.columns:
            del total_results[d]

    total_results.sort_values('# of flooded people', ascending=False, inplace=True)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(output_folder / "summary_results.xlsx", engine='xlsxwriter')
    write_to_sheet_table(writer, total_results[save_cols], 'Results')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


def remove_ini_files():
    for ini_file in ['network.ini', 'analyses.ini']:
        if Ra2ceGUI.current_project.joinpath(ini_file).is_file():
            Ra2ceGUI.current_project.joinpath(ini_file).unlink()


def save_route_names():
    output_folder = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['output']
    project_name = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['project']['name']
    routes_results_path = output_folder / r"multi_link_origin_closest_destination\{}_results_edges.gpkg".format(project_name)
    routes_results = gpd.read_file(routes_results_path)
    warehouses = 'D2'


def runRA2CE_worker(progress_callback):
    Ra2ceGUI.gui.process('Analyzing... Please wait.')
    try:
        assert Ra2ceGUI.ra2ceHandler
    except AssertionError:
        analyzeFeedback("Validate configuration")
        Ra2ceGUI.gui.process('Ready.')
        return

    try:
        assert Ra2ceGUI.floodmap_overlay_feedback == "Overlay done" or Ra2ceGUI.floodmap_overlay_feedback == "Existing overlay shown"
    except AssertionError:
        analyzeFeedback("Overlay flood map")
        Ra2ceGUI.gui.process('Ready.')
        return

    try:
        progress_callback.emit("Running...")
        Ra2ceGUI.ra2ceHandler.input_config.analysis_config.configure()
        Ra2ceGUI.ra2ceHandler.run_analysis()
        logging.info("RA2CE successfully ran. Aggregating results..")
        aggregate_results()
        # save_route_names()
        # remove_ini_files()
        analyzeFeedback("Analysis finished")
        logging.info("Analysis finished.")
    except BaseException as e:
        Ra2ceGUI.gui.process('Ready.')
        logging.error(e)

    Ra2ceGUI.gui.process('Ready.')


def runRA2CE():
    Ra2ceGUI.gui.elements["main_map"]["widget"].threadpool = QThreadPool()
    logging.info("Multithreading with maximum %d threads" % Ra2ceGUI.gui.elements["main_map"]["widget"].threadpool.maxThreadCount())

    worker = Worker(runRA2CE_worker)  # Any other args, kwargs are passed to the run function

    # Execute
    Ra2ceGUI.gui.elements["main_map"]["widget"].threadpool.start(worker)

