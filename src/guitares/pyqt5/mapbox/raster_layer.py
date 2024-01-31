import os
import glob
from PIL import Image
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
import rasterio
import rasterio.features
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio import MemoryFile
from rasterio.transform import Affine
import geopandas as gpd
import pandas as pd
import shapely
#import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import numpy as np

from .colorbar import ColorBar
from guitares.colormap import cm2png

from .layer import Layer

class RasterLayer(Layer):
    def __init__(self, mapbox, id, map_id):
        super().__init__(mapbox, id, map_id)
        self.active = False
        self.type   = "raster"
        self.new    = True
        self.file_name = map_id + ".png"

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


    def clear(self):
        self.active = False
        js_string = "import('/js/main.js').then(module => {module.removeLayer('" + self.map_id + "')});"
        self.mapbox.view.page().runJavaScript(js_string)

    def update(self):
        print("Updating image layer")

    def set_data(self,
                 x=None,
                 y=None,
                 z=None,
                 image_file=None,
                 legend_title="",
                 cmin=None,
                 cmax=None,
                 cstep=None,
                 decimals=None,
                 crs=None,
                 colormap=None):
        
        self.data = {}
        self.data["x"] = x
        self.data["y"] = y
        self.data["z"] = z
        self.data["image_file"] = image_file
        self.data["legend_title"] = legend_title
        self.data["cmin"] = cmin
        self.data["cmax"] = cmax
        self.data["cstep"] = cstep
        self.data["decimals"] = decimals
        self.data["crs"] = crs
        self.data["colormap"] = colormap

        cmap = colormap

        if not crs:
            src_crs = "EPSG:4326"
        else:
            src_crs = "EPSG:" + crs.epsg

        # Web Mercator
        dst_crs = 'EPSG:3857'

        if image_file:

            with rasterio.open(image_file) as src:
                transform, width, height = calculate_default_transform(
                    src.crs, dst_crs, src.width, src.height, *src.bounds)
                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': dst_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })
                # bnds = src.bounds

                mem_file = MemoryFile()
                with mem_file.open(**kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=dst_crs,
                            resampling=Resampling.nearest)

                    band1 = dst.read(1)

            new_bounds = transform_bounds(dst_crs, src_crs,
                                          dst.bounds[0],
                                          dst.bounds[1],
                                          dst.bounds[2],
                                          dst.bounds[3])
            isn = np.where(band1 < 0.001)
            band1[isn] = np.nan

            band1 = np.flipud(band1)
            cminimum = np.nanmin(band1)
            cmaximum = np.nanmax(band1)

            norm = matplotlib.colors.Normalize(vmin=cminimum, vmax=cmaximum)
            vnorm = norm(band1)

            cmap = cm.get_cmap(colormap)
            im = Image.fromarray(np.uint8(cmap(vnorm) * 255))

            overlay_file = "./overlays/" + self.file_name
            im.save(os.path.join(self.mapbox.server_path, overlay_file))

            # Bounds
            bounds = [[new_bounds[0], new_bounds[2]], [new_bounds[3], new_bounds[1]]]
            bounds_string = "[[" + str(bounds[0][0]) + "," + str(bounds[0][1]) + "],[" + str(bounds[1][0]) + "," + str(bounds[1][1]) + "]]"

        else:

            # Color scale
            if self.color_scale_auto:
                if self.color_scale_symmetric:
                    if self.color_scale_symmetric_side == "min":
                        cmin = np.nanmin(z)
                        cmax = -cmin
                    elif self.color_scale_symmetric_side == "max":
                        cmax = np.nanmax(z)
                        cmin = -cmax
                    else:
                        cmx = max(abs(np.nanmin(z)), abs(np.nanmax(z)))
                        cmin = -cmx
                        cmax = cmx
                else:
                    cmin = np.nanmin(z)
                    cmax = np.nanmax(z)
            else:    
                cmin = self.color_scale_cmin
                cmax = self.color_scale_cmax

            ls = LightSource(azdeg=315, altdeg=30)

#            cmap = settings.color_map_earth
#            cmap = matplotlib.pyplot.get_cmap('gist_earth')
            dx = (x[1] - x[0]) / 2
            dy = (y[1] - y[0]) / 2
            rgb = ls.shade(np.flipud(z), cmap,
                           vmin=cmin,
                           vmax=cmax,
                           dx=dx * 50000,
                           dy=dy * 50000,
                           vert_exag=10.0,
                           blend_mode="soft")
            rgb = rgb * 255
            rgb = rgb.astype(np.uint8)

            # First create rasterio image
            res = (x[-1] - x[0]) / (x.size - 1)
            transform = Affine.translation(x[0] - res / 2, y[-1] + res / 2) * Affine.scale(res, -res)
            mem_file1 = MemoryFile()
            src = rasterio.open(
                mem_file1,
                'w',
                driver='GTiff',
                height=y.size,
                width=x.size,
                count=4,
                dtype=rgb.dtype,
                crs=src_crs,
                transform=transform,
            )
            src.write(rgb[:,:,0], 1)
            src.write(rgb[:,:,1], 2)
            src.write(rgb[:,:,2], 3)
            src.write(rgb[:,:,3], 4)

            # Let's convert it to web mercator
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })
            # bnds = src.bounds

            mem_file2 = MemoryFile()
            with mem_file2.open(**kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest)

                bounds = transform_bounds(dst_crs, src_crs,
                                          dst.bounds[0],
                                          dst.bounds[1],
                                          dst.bounds[2],
                                          dst.bounds[3])

                rgb = np.empty([dst.height, dst.width, 4], dtype=np.uint8)
                rgb[:,:,0] = dst.read(1)
                rgb[:,:,1] = dst.read(2)
                rgb[:,:,2] = dst.read(3)
                rgb[:,:,3] = dst.read(4)
                im = Image.fromarray(rgb, "RGBA")

                overlay_file = "./overlays/" + self.file_name
                im.save(os.path.join(self.mapbox.server_path, "overlays", self.file_name))

                # Bounds
                bounds_string = "[[" + str(bounds[0]) + "," + str(bounds[2]) + "],[" + str(bounds[1]) + "," + str(bounds[3]) + "]]"


                # Delete old legend files
                for file_name in glob.glob(os.path.join(self.mapbox.server_path, "overlays", self.map_id + ".legend.*.png")):
                    try:
                        os.remove(file_name)
                    except:
                        pass

                # add random integer string to legend file to force reload                
                # create string with random integer between 1 and 1,000,000
                rstring = str(np.random.randint(1, 1000000))
                legend_file = self.map_id + ".legend." + rstring + ".png"
                cm2png(cmap,
                    file_name = os.path.join(self.mapbox.server_path, "overlays", legend_file),
                    orientation="vertical",
                    vmin=cmin,
                    vmax=cmax)

        # Legend
        clrbar = ColorBar(colormap=colormap, legend_title=legend_title)
        clrbar.make(cmin, cmax, cstep=cstep, decimals=decimals)
        clrmap_string = clrbar.to_json()

        clrmap_string = "'./overlays/" + legend_file + "'"

        if self.new:
            js_string = "import('/js/image_layer.js').then(module => {module.addLayer('" + overlay_file + "','" + self.map_id + "'," + bounds_string + "," + clrmap_string + ")});"
            self.mapbox.view.page().runJavaScript(js_string)
        else:
            js_string = "import('/js/image_layer.js').then(module => {module.updateLayer('" + overlay_file + "','" + self.map_id + "'," + bounds_string + "," + clrmap_string + ")});"
            self.mapbox.view.page().runJavaScript(js_string)
        self.mapbox.runjs("/js/image_layer.js", "setOpacity", arglist=[self.map_id, self.opacity, self.side])

        self.new = False

    def redraw(self):
        if self.data:
            self.new = True
            self.set_data(x=self.data["x"],
                          y=self.data["y"],
                          z=self.data["z"],
                          image_file=self.data["image_file"],
                          legend_title=self.data["legend_title"],
                          cmin=self.data["cmin"],
                          cmax=self.data["cmax"],
                          cstep=self.data["cstep"],
                          decimals=self.data["decimals"],
                          crs=self.data["crs"],
                          colormap=self.data["colormap"])
        if not self.get_visibility():
            self.set_visibility(False)
        
