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
           label_size=8,
           tick_size=6,
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
        ax = fig.add_axes([0.05, 0.80, 0.9, 0.12])
    else:
        fig = plt.figure(figsize=(width, height))
        ax = fig.add_axes([0.80, 0.05, 0.12, 0.90])

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cb = mpl.colorbar.ColorbarBase(ax,
                                   cmap=cmap,
                                   norm=norm,
                                   orientation=orientation)


    cb.ax.tick_params(labelsize=tick_size)
    cb.set_label(legend_label, size=label_size)
    if legend_label != "":
        cb.set_label(legend_label, fontsize=6, labelpad=3)  # initial label
        cb.ax.yaxis.set_label_position('left')  # put label on left side
        cb.ax.yaxis.set_tick_params(labelsize=6)  # optional: set tick font size

    if decimals > -1:
        cb.formatter = mpl.ticker.FormatStrFormatter(f'%.{decimals}f')  # set decimals
        cb.update_ticks()

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
