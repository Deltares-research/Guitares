"""Colormap utilities for reading, registering, and exporting colormaps as PNG images."""

import os
from typing import List

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def read_color_maps(path_name: str) -> List[str]:
    """Read all colormaps from a folder and register them with matplotlib.

    Each ``.txt`` file in the folder is expected to contain whitespace-separated
    RGB values (one row per colour stop).  After registration the colormaps are
    available via ``matplotlib.colormaps``.

    Parameters
    ----------
    path_name : str
        Path to the directory containing colormap text files.

    Returns
    -------
    List[str]
        List of all registered colormap names (including newly added ones).
    """
    files = os.listdir(path_name)
    for file in files:
        if file.endswith(".txt"):
            name = os.path.splitext(file)[0]
            rgb = read_colormap(os.path.join(path_name, file))
            cmap = mpl.colors.ListedColormap(rgb, name=name)
            mpl.colormaps.register(cmap=cmap)
    return plt.colormaps()


def cm2png(
    cmap: mpl.colors.Colormap,
    file_name: str = "colorbar.png",
    orientation: str = "horizontal",
    vmin: float = 0.0,
    vmax: float = 1.0,
    legend_title: str = "",
    legend_label: str = "",
    label_size: int = 8,
    tick_size: int = 6,
    units: str = "",
    unit_string: str = "",
    decimals: int = -1,
    width: float = 2.5,
    height: float = 1.0,
) -> None:
    """Create a high-resolution PNG image of a colorbar with transparent background.

    Parameters
    ----------
    cmap : mpl.colors.Colormap
        Matplotlib colormap to render.
    file_name : str, optional
        Output file path, by default ``"colorbar.png"``.
    orientation : str, optional
        ``"horizontal"`` or ``"vertical"``, by default ``"horizontal"``.
    vmin : float, optional
        Minimum data value for the colorbar, by default 0.0.
    vmax : float, optional
        Maximum data value for the colorbar, by default 1.0.
    legend_title : str, optional
        Title displayed above the colorbar.
    legend_label : str, optional
        Label displayed alongside the colorbar.
    label_size : int, optional
        Font size for the label, by default 8.
    tick_size : int, optional
        Font size for tick labels, by default 6.
    units : str, optional
        Unit string (currently unused).
    unit_string : str, optional
        Alternative unit string (currently unused).
    decimals : int, optional
        Number of decimal places for tick labels. Values < 0 use default
        formatting, by default -1.
    width : float, optional
        Figure width in inches, by default 2.5.
    height : float, optional
        Figure height in inches, by default 1.0.

    Returns
    -------
    None
    """
    plt.ioff()

    # Render at 3x size and high DPI so the browser scales down crisply
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
    cb = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation=orientation)

    cb.ax.tick_params(labelsize=tick_size * scale)
    if legend_label != "":
        cb.set_label(legend_label, fontsize=6 * scale, labelpad=3 * scale)
        cb.ax.yaxis.set_label_position("left")

    if decimals > -1:
        cb.formatter = mpl.ticker.FormatStrFormatter(f"%.{decimals}f")
        cb.update_ticks()

    fig.savefig(
        file_name,
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0.02,
        transparent=True,
        facecolor="none",
        edgecolor="none",
    )
    plt.close(fig)


def read_colormap(file_name: str) -> np.ndarray:
    """Read a single colormap from a whitespace-separated text file.

    Parameters
    ----------
    file_name : str
        Path to a text file with three columns (r, g, b).

    Returns
    -------
    np.ndarray
        Array of shape ``(N, 3)`` with RGB values.
    """
    df = pd.read_csv(
        file_name, index_col=False, header=None, sep=r"\s+", names=["r", "g", "b"]
    )
    v = df.to_numpy()
    return v
