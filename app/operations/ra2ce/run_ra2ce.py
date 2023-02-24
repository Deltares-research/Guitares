# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThreadPool
from src.guitools.pyqt5.worker import Worker
from ra2ceGUI.ra2ceGUI_base import Ra2ceGUI
import geopandas as gpd
import pandas as pd
import pickle

dest_temp = {'Health facility': 'D1', 'HSA Warehouse': 'D2', 'Market': 'D3'}
rename_temp = {'EV1_ma_AD1': 'Health facility access',
               'EV1_ma_AD2': 'HSA Warehouse access',
               'EV1_ma_AD3': 'Market access'}


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


def read_pickle(path):
    with open(path, 'rb') as file:
        f = pickle.load(file)
    return f


def aggregate_results():
    #"D:\RA2CE\1_data\fullTest\output\multi_link_origin_closest_destination\fullTest_optimal_routes_with_hazard.gpkg"
    output_folder = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['output']
    village_ids = Ra2ceGUI.ra2ce_config['base_data']['path'].joinpath('network', 'village_ids.pickle')
    project_name = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['project']['name']
    origins_path = output_folder / r"multi_link_origin_closest_destination\{}_origins.gpkg".format(project_name)
    origins = gpd.read_file(origins_path)

    id_to_vilname = read_pickle(village_ids)
    origins['FID'] = origins['o_id'].apply(lambda x: int(x.split("_")[-1]))
    origins['VIL_NAME'] = origins['FID'].map(id_to_vilname)
    if 'POI' in origins.columns:
        del origins["POI"]

    origins.rename(columns=rename_temp, inplace=True)

    flooded_results_path = output_folder / "buildings_flooded.csv"
    flooded_results = pd.read_csv(flooded_results_path)
    total_results = pd.merge(flooded_results, origins, on="VIL_NAME")
    for d in ['o_id', 'cnt', 'geometry', 'FID']:
        del total_results[d]

    # Sum the damages over the totals per Event, RP, EAD and aggregation labels
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(output_folder / "summary_results.xlsx", engine='xlsxwriter')
    write_to_sheet_table(writer, total_results, 'Results')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

def save_route_names():
    output_folder = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['output']
    project_name = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['project']['name']
    routes_results_path = output_folder / r"multi_link_origin_closest_destination\{}_results_edges.gpkg".format(project_name)
    routes_results = gpd.read_file(routes_results_path)
    warehouses = 'D2'


def runRA2CE():
    # self.threadpool = QtCore.QThreadPool()
    # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())



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
        # save_route_names()
        analyzeFeedback("Analysis finished")
        print("RA2CE successfully ran.")
    except BaseException as e:
        print(e)
