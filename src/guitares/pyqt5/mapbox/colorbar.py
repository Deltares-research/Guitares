#import os
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
    def __init__(self, colormap="jet", scale="linear", orientation="vertical", legend_title="", color_values=None):
        self.title       = legend_title
        self.orientation = orientation
        self.color_map   = colormap
        self.scale       = scale
        self.contour     = []
        self.color_values = color_values
            

    def make(self,
             cmin,
             cmax,
             cstep=None,
             decimals=None,
             reverse=True):
        
        if self.color_values:
            for val in self.color_values:

                zl = val["lower_value"]
                zu = val["upper_value"]

                if decimals:
                    zu = np.around(zu, decimals)
                    zl = np.around(zl, decimals)

                zustr = str(zu)
                zlstr = str(zl)

                if decimals==0:
                    zustr = str(int(zu))
                    zlstr = str(int(zl))
                elif decimals is not None:
                    zustr = str(np.around(zu, decimals))
                    zlstr = str(np.around(zl, decimals))

                contour = {}
                if "string" in val:
                    contour["string"] = val["string"]
                else:    
                    if zu>1.0e7:
                        contour["string"] = "> " + zlstr
                    elif zl<-1.0e7:
                        contour["string"] = "< " + zustr
                    else:    
                        contour["string"] = zlstr + " - " + zustr

                contour["lower_value"] = zl
                contour["upper_value"] = zu

                contour["rgb"] = val["rgb"]
                contour["hex"] = rgb2hex(tuple(val["rgb"]))

                self.contour.append(contour)

        else:    

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

                    if decimals==0:
                        zustr = str(int(zu))
                        zlstr = str(int(zl))
                    elif decimals is not None:
                        zustr = str(np.around(zu, decimals))
                        zlstr = str(np.around(zl, decimals))

                    contour = {}
                    if i == 0:
    #                    contour["string"] = "< " + str(cmin)
                        contour["string"] = "< " + zustr
                        contour["lower_value"] = -1.0e6
                        contour["upper_value"] = zu
                    elif i == nsteps - 1:
    #                    contour["string"] = "> " + str(cmax)
                        contour["string"] = "> " + zlstr
                        contour["lower_value"] = zl
                        contour["upper_value"] = 1.0e6
                    else:
                        contour["string"] = zlstr + " - " + zustr
                        contour["lower_value"] = zl
                        contour["upper_value"] = zu
                    contour["rgb"] = rgb
                    contour["hex"] = rgb2hex(tuple(rgb))

                    self.contour.append(contour)

            if reverse:
                self.contour.reverse()


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

    def to_dict(self):
        jsn = {}
        jsn["title"] = self.title
        jsn["contour"] = []
        for cnt in self.contour:
            contour= {}
            contour["text"] = cnt["string"]
            contour["color"] = "#" + cnt["hex"]
            jsn["contour"].append(contour)
        return jsn

def rgb2hex(rgb):
    return '%02x%02x%02x' % rgb

