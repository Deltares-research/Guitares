import os
import glob
from PIL import Image
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
import rasterio
# import rasterio.features
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio import MemoryFile
# from rasterio.transform import Affine
from matplotlib.colors import LightSource
import numpy as np
import copy
import xarray as xr
from pyproj import Transformer

from .colorbar import ColorBar
from guitares.colormap import cm2png

from .layer import Layer

class RasterLayer(Layer):
    def __init__(self, map, id, map_id):
        super().__init__(map, id, map_id)
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
        self.map.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])

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
            src_crs = "EPSG:" + str(crs.to_epsg())

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
            im.save(os.path.join(self.map.server_path, overlay_file))

            # Bounds
            bounds = [[new_bounds[0], new_bounds[2]], [new_bounds[3], new_bounds[1]]]

        else:

            # Color scale
            if self.color_scale_auto:
                if self.color_scale_symmetric:
                    if self.color_scale_symmetric_side == "min":
                        cmin = np.nanmin(z)
                        if cmin > 0:
                            cmin = -cmin
                        cmax = -cmin
                    elif self.color_scale_symmetric_side == "max":
                        cmax = np.nanmax(z)
                        if cmax < 0:
                            cmax = -cmax
                        cmin = -cmax
                    else:
                        cmx = max(abs(np.nanmin(z)), abs(np.nanmax(z)))
                        cmin = -cmx
                        cmax = cmx
                else:
                    cmin = np.nanmin(z)
                    cmax = np.nanmax(z)
                if cmax < cmin + 0.01:
                    cmin = -0.01
                    cmax = 0.01    
            else:    
                cmin = self.color_scale_cmin
                cmax = self.color_scale_cmax

            if self.hillshading:
                ls = LightSource(azdeg=315, altdeg=30)
                dx = (x[1] - x[0]) / 2
                dy = (y[1] - y[0]) / 2
                rgb = ls.shade(np.flipud(z), cmap,
                            vmin=cmin,
                            vmax=cmax,
                            dx=dx * 0.5,
                            dy=dy * 0.5,
                            vert_exag=10.0,
                            blend_mode="soft")
                rgb = rgb * 255

            else:
                norm = matplotlib.colors.Normalize(vmin=cmin, vmax=cmax)
                vnorm = norm(np.flipud(z))
                cmap = cm.get_cmap(colormap)
                rgb = cmap(vnorm) * 255

            # Create xarray DataArray with RGBA values of the rgb array
            rgba_da = xr.DataArray(np.transpose(rgb, (2, 0, 1)),
                                dims=["band", "y", "x"],
                                coords={ "band": [0, 1, 2, 3], "y": np.flip(y), "x": x})

            # 1. Assign CRS and spatial dims
            rgba_da.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
            rgba_da.rio.write_crs(src_crs, inplace=True)  # e.g., EPSG:32633

            # 2. Reproject to Web Mercator
            rgba_3857 = rgba_da.rio.reproject("EPSG:3857")

            # 3. Export as PNG
            # Convert to uint8 and rearrange shape for Pillow
            # There may be NaN values in the data that cannot be converted to uint8
            # So we need to fill them with 0 (transparent)
            # and convert to uint8
            rgba_3857 = rgba_3857.fillna(0)
            rgba_3857 = rgba_3857.clip(min=0, max=255)
            # Convert to uint8
            img_data = rgba_3857.values.astype(np.uint8)  # shape: (height, width, 4)

            # In case of xarray with shape (band, y, x)
            if img_data.shape[0] == 4:
                img_data = np.transpose(img_data, (1, 2, 0))  # to (y, x, 4)

            image = Image.fromarray(img_data, mode="RGBA")

            # overlay_file = os.path.join(self.map.server_path, "testing.png")
            image.save(os.path.join(self.map.server_path, "overlays", self.file_name))

            # Get bounds in EPSG:3857
            left, bottom, right, top = rgba_3857.rio.bounds()

            # Reproject bounds to EPSG:4326
            transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
            west, south = transformer.transform(left, bottom)
            east, north = transformer.transform(right, top)

            overlay_file = "./overlays/" + self.file_name

            # It's possible that the dst.bounds cover the entire globe, and that bounds will
            # then run from 179.888 to 179.999
            # In that case bounds[0][0] = bounds[0][0] - 360.0
            if left < -19800000.0 and right > 19800000.0:
                if west > 0.0:
                    west = -180.0
                if east < 0.0:
                    east = 180.0    

            if west > east:
                west -= 360.0
            if west < -180.0:
                west += 360.0
                east += 360.0

            # Delete old legend files
            for file_name in glob.glob(os.path.join(self.map.server_path, "overlays", self.map_id + ".legend.*.png")):
                try:
                    os.remove(file_name)
                except:
                    pass

            # add random integer string to legend file to force reload                
            # create string with random integer between 1 and 1,000,000
            rstring = str(np.random.randint(1, 1000000))
            legend_file = self.map_id + ".legend." + rstring + ".png"
            width = 1.0
            height = 2.0
            cm2png(cmap,
                file_name = os.path.join(self.map.server_path, "overlays", legend_file),
                orientation="vertical",
                vmin=cmin,
                vmax=cmax,
                width=width,
                height=height)

            # Legend
            clrbar = ColorBar(colormap=colormap, legend_title=legend_title)
            clrbar.make(cmin, cmax, cstep=cstep, decimals=decimals)
            clrmap_string = clrbar.to_json()

            clrmap_string = "./overlays/" + legend_file

        # print(bounds)

        if east > 180.0:
            # Image crosses date line
            # Need to create two images, west and east
            # First read in the png file
            im = Image.open(os.path.join(self.map.server_path, overlay_file))
            # find pixel index
            npixx = im.size[0]
            dlon = east - west
            ipixx = int(npixx * (180.0 - west) / dlon)
            im1 = im.crop((0, 0, ipixx, im.size[1]))
            im2 = im.crop((ipixx + 1, 0, im.size[0], im.size[1]))
            im1.save(os.path.join(self.map.server_path, overlay_file.replace(".png", ".a.png")))
            im2.save(os.path.join(self.map.server_path, overlay_file.replace(".png", ".b.png")))
            overlay_file_a = overlay_file.replace(".png", ".a.png")
            overlay_file_b = overlay_file.replace(".png", ".b.png")

            west_a = west
            east_a = 180.0
            west_b = -180.0
            east_b = east - 360.0

            bounds_a = [[west_a, east_a], [south, north]]
            bounds_b = [[west_b, east_b], [south, north]]

            split_image = True
        else:
            bounds = [[west, east], [south, north]]
            split_image = False

        if self.new:

            # First time we add the layer, so we need to create it. Always create both west and east layers.

            # Add west layer
            self.map.runjs("/js/image_layer.js", "addLayer", arglist=[self.map_id + ".a", self.side])
            # Add east layer
            self.map.runjs("/js/image_layer.js", "addLayer", arglist=[self.map_id + ".b", self.side])

        if split_image:

            # Make the east layer visible
            self.map.runjs(self.main_js, "showLayer", arglist=[self.map_id + ".b", self.side])

            # Now we need to update the layers with the new bounds and opacity
            self.map.runjs("/js/image_layer.js", "updateLayer", arglist=[overlay_file_a,
                                                                         self.map_id + ".a",                                                                        
                                                                         bounds_a,
                                                                         clrmap_string])
            self.map.runjs("/js/image_layer.js",
                           "setOpacity",
                           arglist=[self.map_id + ".a", self.opacity, self.side])

            self.map.runjs("/js/image_layer.js", "updateLayer", arglist=[overlay_file_b,
                                                                         self.map_id + ".b",                                                                        
                                                                         bounds_b,
                                                                         ""])
            self.map.runjs("/js/image_layer.js",
                           "setOpacity",
                           arglist=[self.map_id + ".b", self.opacity, self.side])

        else:
            # Just update the layer with the new bounds and opacity
            self.map.runjs("/js/image_layer.js", "updateLayer", arglist=[overlay_file,
                                                                         self.map_id + ".a",                                                                         
                                                                         bounds,
                                                                         clrmap_string])
            self.map.runjs("/js/image_layer.js",
                           "setOpacity",
                           arglist=[self.map_id + ".a", self.opacity, self.side])

            # Make the east layer invisible
            self.map.runjs(self.main_js, "hideLayer", arglist=[self.map_id + ".b", self.side])

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
        
