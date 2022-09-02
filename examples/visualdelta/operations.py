from visualdelta import visualdelta
import pandas as pd
import numpy as np


def add_option():

    # Update all GUI elements
    visualdelta.gui.update()

def calculate_slr(year):
    slr_ts = pd.read_csv('slr\\SLR_245.csv', index_col=0, header=0)
    slr_val = np.interp(year,slr_ts.index, slr_ts['0.5'])
    slr_low = np.interp(year,slr_ts.index, slr_ts['0.17'])
    slr_high = np.interp(year, slr_ts.index, slr_ts['0.83'])
    print('Median SLR for SSP2-4.5 in year {} is {:.2f} (likely range {:.2f} - {:.2f})'.format(year,slr_val, slr_low, slr_high))