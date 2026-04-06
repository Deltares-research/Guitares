"""Discrete color-bar legend builder for map overlays.

Provides ``ColorBar`` for constructing step-wise legends from either
explicit color-value bins or a Matplotlib colormap, and ``MplColorHelper``
for mapping scalar values to RGB via a Matplotlib colormap.
"""

import json
from typing import Any, Dict, List, Optional, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm


class MplColorHelper:
    """Map scalar values to RGB colours via a Matplotlib colormap.

    Parameters
    ----------
    cmap_name : str
        Name of a registered Matplotlib colormap.
    start_val : float
        Lower bound of the normalisation range.
    stop_val : float
        Upper bound of the normalisation range.
    """

    def __init__(self, cmap_name: str, start_val: float, stop_val: float) -> None:
        self.cmap_name = cmap_name
        self.cmap = plt.get_cmap(cmap_name)
        self.norm = mpl.colors.Normalize(vmin=start_val, vmax=stop_val)
        self.scalarMap = cm.ScalarMappable(norm=self.norm, cmap=self.cmap)

    def get_rgb(self, val: float) -> List[int]:
        """Return the RGB colour for *val* as a list of three 0--255 integers.

        Parameters
        ----------
        val : float
            Scalar value within the normalisation range.

        Returns
        -------
        list of int
            ``[R, G, B]`` each in the range 0--255.
        """
        rgb0 = self.scalarMap.to_rgba(val)
        rgb = [0, 0, 0]
        rgb[0] = round(rgb0[0] * 255)
        rgb[1] = round(rgb0[1] * 255)
        rgb[2] = round(rgb0[2] * 255)
        return rgb


class ColorBar:
    """Discrete step-wise colour-bar legend.

    Parameters
    ----------
    colormap : str
        Matplotlib colormap name.
    scale : str
        Scale type (currently only ``"linear"`` is implemented).
    orientation : str
        ``"vertical"`` or ``"horizontal"``.
    legend_title : str
        Title text displayed above the legend.
    color_values : list of dict, optional
        Explicit bin definitions with ``lower_value``, ``upper_value``,
        ``rgb``, and optionally ``string`` keys.
    """

    def __init__(
        self,
        colormap: str = "jet",
        scale: str = "linear",
        orientation: str = "vertical",
        legend_title: str = "",
        color_values: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.title = legend_title
        self.orientation = orientation
        self.color_map = colormap
        self.scale = scale
        self.contour: List[Dict[str, Any]] = []
        self.color_values = color_values

    def make(
        self,
        cmin: float,
        cmax: float,
        cstep: Optional[float] = None,
        decimals: Optional[int] = None,
        reverse: bool = True,
    ) -> None:
        """Build the contour entries for the colour bar.

        Parameters
        ----------
        cmin : float
            Minimum value of the colour scale.
        cmax : float
            Maximum value of the colour scale.
        cstep : float, optional
            Step size between contour levels.  Defaults to ``(cmax - cmin) / 20``.
        decimals : int, optional
            Number of decimal places for tick labels.
        reverse : bool
            If *True* (default), reverse the contour order.
        """

        if self.color_values:
            for val in self.color_values:
                zl = val["lower_value"]
                zu = val["upper_value"]

                if decimals:
                    zu = np.around(zu, decimals)
                    zl = np.around(zl, decimals)

                zustr = str(zu)
                zlstr = str(zl)

                if decimals == 0:
                    zustr = str(int(zu))
                    zlstr = str(int(zl))
                elif decimals is not None:
                    zustr = str(np.around(zu, decimals))
                    zlstr = str(np.around(zl, decimals))

                contour: Dict[str, Any] = {}
                if "string" in val:
                    contour["string"] = val["string"]
                else:
                    if zu > 1.0e7:
                        contour["string"] = f"> {zlstr}"
                    elif zl < -1.0e7:
                        contour["string"] = f"< {zustr}"
                    else:
                        contour["string"] = f"{zlstr} - {zustr}"

                contour["lower_value"] = zl
                contour["upper_value"] = zu

                contour["rgb"] = val["rgb"]
                contour["hex"] = rgb2hex(tuple(val["rgb"]))

                self.contour.append(contour)

        else:
            if np.isnan(cmin) or np.isnan(cmax):
                return

            clmap = MplColorHelper(self.color_map, cmin, cmax)

            if self.scale == "linear":
                if not cstep:
                    cstep = (cmax - cmin) / 20

                nsteps = round((cmax - cmin) / cstep + 2)

                for i in range(nsteps):
                    # Interpolate
                    zl = cmin + (i - 1) * cstep
                    zu = zl + cstep
                    z = 0.5 * (zl + zu)
                    rgb = clmap.get_rgb(z)

                    if decimals:
                        zu = np.around(zu, decimals)
                        zl = np.around(zl, decimals)

                    zustr = str(zu)
                    zlstr = str(zl)

                    if decimals == 0:
                        zustr = str(int(zu))
                        zlstr = str(int(zl))
                    elif decimals is not None:
                        zustr = str(np.around(zu, decimals))
                        zlstr = str(np.around(zl, decimals))

                    contour = {}
                    if i == 0:
                        contour["string"] = f"< {zustr}"
                        contour["lower_value"] = -1.0e6
                        contour["upper_value"] = zu
                    elif i == nsteps - 1:
                        contour["string"] = f"> {zlstr}"
                        contour["lower_value"] = zl
                        contour["upper_value"] = 1.0e6
                    else:
                        contour["string"] = f"{zlstr} - {zustr}"
                        contour["lower_value"] = zl
                        contour["upper_value"] = zu
                    contour["rgb"] = rgb
                    contour["hex"] = rgb2hex(tuple(rgb))

                    self.contour.append(contour)

            if reverse:
                self.contour.reverse()

    def to_json(self) -> str:
        """Serialise the colour bar to a JSON string.

        Returns
        -------
        str
            JSON representation with ``title`` and ``contour`` keys.
        """
        return json.dumps(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """Return the colour bar as a plain dictionary.

        Returns
        -------
        dict
            Dictionary with ``title`` and ``contour`` keys.
        """
        jsn: Dict[str, Any] = {}
        jsn["title"] = self.title
        jsn["contour"] = []
        for cnt in self.contour:
            contour = {}
            contour["text"] = cnt["string"]
            contour["color"] = f"#{cnt['hex']}"
            jsn["contour"].append(contour)
        return jsn


def rgb2hex(rgb: Tuple[int, int, int]) -> str:
    """Convert an ``(R, G, B)`` tuple (0--255 each) to a hex string.

    Parameters
    ----------
    rgb : tuple of int
        ``(R, G, B)`` colour values.

    Returns
    -------
    str
        Six-character hex string (without ``#`` prefix).
    """
    return "%02x%02x%02x" % rgb
