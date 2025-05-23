# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 10:08:26 2021

@author: ormondt
"""

import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

def read_color_maps(path_name):
    """Read all colormaps from a folder and register them (add them to matplotlib.colormaps). Return list of colormap names."""    
    # Get list of files in path
    files = os.listdir(path_name)    
    # Loop over files
    for file in files:
        if file.endswith(".txt"):
            # Name is filename without extension
            name = os.path.splitext(file)[0]
            # Read colormap
            rgb = read_colormap(os.path.join(path_name, file))
            cmap = mpl.colors.ListedColormap(rgb, name=name)
            mpl.colormaps.register(cmap=cmap)
    return plt.colormaps()    


def cm2png(cmap,
           file_name="colorbar.png",
           orientation="horizontal",
           vmin=0.0,
           vmax=1.0,
           legend_title="",
           legend_label="",
           units="",
           unit_string="",
           decimals=-1,
           width=2.5,
           height=1.0):

    """Create png image of colormap"""
    plt.ioff()
    # Create figure
    if orientation == "horizontal":
        fig = plt.figure(figsize=(width, height))
        ax = fig.add_axes([0.05, 0.80, 0.9, 0.15])
    else:
        fig = plt.figure(figsize=(width, height))
        ax = fig.add_axes([0.80, 0.05, 0.15, 0.90])

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cb = mpl.colorbar.ColorbarBase(ax,
                                   cmap=cmap,
                                   norm=norm,
                                   orientation=orientation,
                                   label=legend_label)
    cb.ax.tick_params(labelsize=6)

    # Save figure
    fig.savefig(file_name, dpi=150, bbox_inches='tight')
    plt.close(fig)

def read_colormap(file_name):
    df = pd.read_csv(file_name,
                     index_col=False,
                     header=None,
                     sep=r'\s+',
                     names=['r','g','b'])
    v = df.to_numpy()
    return v
