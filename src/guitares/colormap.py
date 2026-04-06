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
    """Create a high-resolution PNG image of a colorbar with transparent background."""
    plt.ioff()

    # Render at 3× size and high DPI so the browser scales down crisply
    scale = 3
    dpi = 200

    if orientation == "horizontal":
        fig = plt.figure(figsize=(width * scale, height * scale))
        ax = fig.add_axes([0.05, 0.80, 0.9, 0.12])
    else:
        fig = plt.figure(figsize=(width * scale, height * scale))
        ax = fig.add_axes([0.80, 0.05, 0.12, 0.90])

    # Transparent background
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cb = mpl.colorbar.ColorbarBase(ax,
                                   cmap=cmap,
                                   norm=norm,
                                   orientation=orientation)

    cb.ax.tick_params(labelsize=tick_size * scale)
    if legend_label != "":
        cb.set_label(legend_label, fontsize=6 * scale, labelpad=3 * scale)
        cb.ax.yaxis.set_label_position('left')

    if decimals > -1:
        cb.formatter = mpl.ticker.FormatStrFormatter(f'%.{decimals}f')
        cb.update_ticks()

    fig.savefig(file_name, dpi=dpi, bbox_inches='tight', pad_inches=0.02,
                transparent=True, facecolor='none', edgecolor='none')
    plt.close(fig)

def read_colormap(file_name):
    df = pd.read_csv(file_name,
                     index_col=False,
                     header=None,
                     sep=r'\s+',
                     names=['r','g','b'])
    v = df.to_numpy()
    return v
