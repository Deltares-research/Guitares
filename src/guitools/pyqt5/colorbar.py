# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.
#
# This tool is developed for demonstration purposes only.

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
import json

class MplColorHelper:

  def __init__(self, cmap_name, start_val, stop_val):
    self.cmap_name = cmap_name
    self.cmap = plt.get_cmap(cmap_name)
    self.norm = mpl.colors.Normalize(vmin=start_val, vmax=stop_val)
    self.scalarMap = cm.ScalarMappable(norm=self.norm, cmap=self.cmap)

  def get_rgb(self, val):
      rgb0   = self.scalarMap.to_rgba(val)
      rgb    = [0, 0, 0]
      rgb[0] = round(rgb0[0] * 255)
      rgb[1] = round(rgb0[1] * 255)
      rgb[2] = round(rgb0[2] * 255)
      return rgb

class ColorBar:
    def __init__(self, colormap="jet", scale="linear", orientation="vertical", legend_title=""):
        self.title       = legend_title
        self.orientation = orientation
        self.color_map   = colormap
        self.scale       = scale
        self.contour     = []

    def make(self,
             cmin,
             cmax,
             cstep=None,
             decimals=None,
             reverse=True):

        clmap = MplColorHelper(self.color_map, cmin, cmax)

        if self.scale == "linear":
            if not cstep:
                cstep = (cmax - cmax) / 10

            nsteps = round((cmax - cmin) / cstep + 2)

            for i in range(nsteps):

                # Interpolate
                zl = cmin + (i - 1) * cstep
                zu = zl + cstep
                z = 0.5 * (zl + zu)
                rgb = clmap.get_rgb(z)

                if decimals:
                    zl = np.around(zl, decimals)
                    zu = np.around(zu, decimals)

                contour = {}
                if i == 0:
                    contour["string"] = "< " + str(cmin)
                    contour["lower_value"] = -1.0e6
                    contour["upper_value"] = zu
                elif i == nsteps - 1:
                    contour["string"] = "> " + str(cmax)
                    contour["lower_value"] = zl
                    contour["upper_value"] = 1.0e6
                else:
                    contour["string"] = str(zl) + " - " + str(zu)
                    contour["lower_value"] = zl
                    contour["upper_value"] = zu
                contour["rgb"] = rgb
                contour["hex"] = rgb2hex(tuple(rgb))

                self.contour.append(contour)

            if reverse:
                self.contour.reverse()
        elif self.scale == "discrete":
            if not cstep:
                cstep = (cmax - cmax) / 10

            nsteps = round((cmax - cmin) / cstep + 1)

            for i in range(nsteps):
                # Interpolate
                step = cmin + i * cstep

                if step == 0:
                    continue

                rgb = clmap.get_rgb(step)

                contour = {}
                contour["string"] = str(step)
                contour["value"] = step
                contour["rgb"] = rgb
                contour["hex"] = rgb2hex(tuple(rgb))

                self.contour.append(contour)

    def to_json(self):
        jsn = {}
        jsn["title"] = self.title
        jsn["contour"] = []
        for cnt in self.contour:
            contour= {}
            contour["text"] = cnt["string"]
            contour["color"] = "#" + cnt["hex"]
            jsn["contour"].append(contour)
        return json.dumps(jsn)


def rgb2hex(rgb):
    return '%02x%02x%02x' % rgb

