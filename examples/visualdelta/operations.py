from visualdelta import visualdelta
import pandas as pd
import numpy as np


def add_option():

    # Update all GUI elements
    visualdelta.gui.update()

def calculate_slr():
    ssp = visualdelta.gui.getvar("visualdelta", "ssp")
    year = visualdelta.gui.getvar("visualdelta", "year")
    slr_ts = pd.read_csv('slr\\SLR_{}.csv'.format(ssp), index_col=0, header=0)
    slr_val = np.interp(year,slr_ts.index, slr_ts['0.5'])
    slr_low = np.interp(year,slr_ts.index, slr_ts['0.17'])
    slr_high = np.interp(year, slr_ts.index, slr_ts['0.83'])
    # print('Median SLR for SSP{} in year {} is {:.2f} (likely range {:.2f} - {:.2f})'.format(ssp,year,slr_val, slr_low, slr_high))
    visualdelta.gui.setvar("visualdelta", "year", year)
    visualdelta.gui.setvar("visualdelta", "slr", round(slr_val,2))
    visualdelta.gui.setvar("visualdelta", "slr_string", "{} m ({} - {} m)".format(round(slr_val,2),round(slr_low,2),round(slr_high,2)))

    # Update all GUI elements
    visualdelta.gui.update()