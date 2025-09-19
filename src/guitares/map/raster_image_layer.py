import os
import glob
from PIL import Image
import matplotlib
from matplotlib import cm
import rasterio
from matplotlib.colors import LightSource
import numpy as np
import rioxarray
import xarray as xr
from pyproj import Transformer

from guitares.colormap import cm2png
from .layer import Layer

# This is a combo of image_layer.py and raster_layer.py

class RasterImageLayer(Layer):
    def __init__(self, map, id, map_id, **kwargs):
        super().__init__(map, id, map_id, **kwargs)
        self.active = False
        self.type   = "raster"
        self.new    = True
        self.file_name = map_id + ".png"
        self.data_has_map_overlay = False
        self.rgb = False # True if data is RGB

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def clear(self):
        self.active = False
        self.map.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])
        self.new = True

    def set_data(self, data):

        # data can be either a:
        #     1) file path (in case of a GeoTIFF file)
        #     2) rioxarray.DataArray
        #     3) object that has a make_overlay method (this method should create a png file and return True/False)
        #     4) a method to get the data (this method should return a rioxarray DataArray)

        # Furthermore, type of data can be a scalar field, or RGB

        self.data_has_map_overlay = False
        self.data_has_overview_levels = False

        if isinstance(data, (str, os.PathLike)):
            # 1) file path
            # Read the image file (lazily)
            self.data = data
            # self.data = rioxarray.open_rasterio(data)
            with rasterio.open(data) as src:
                ovr = src.overviews(1)
                if len(ovr) > 0:
                    self.data_has_overview_levels = True
                else:
                    self.data_has_overview_levels = False
            # Check for overview levels
            # self.overview_level, _ = get_appropriate_overview_level(self.data, 1000)
            # If self.data has 3 or 4 bands, then it's RGB(A)
            # if self.data.shape[0] == 3 or self.data.shape[0] == 4:
            #     self.rgb = True

        elif hasattr(data, "rio") and hasattr(data.rio, "reproject"):
            # 2) rioxarray.DataArray
            self.data = data

        elif hasattr(data, "map_overlay") and callable(getattr(data, "map_overlay")):
            # 3) object that has a map_overlay method
            self.data = data
            self.data_has_map_overlay = True

        elif callable(data):
            # 4) a method to get the data
            # self.data = rioxarray.DataArray()
            self.get_data = data

        else:
            raise ValueError("Data must be either a file path, a rioxarray DataArray, or an object with a make_overlay method")

        self.update()

    def update(self):

        # Method is called whenever the map view changes (zoom or pan)

        coords = self.map.map_extent
        lonlim = [coords[0][0], coords[1][0]]
        latlim = [coords[0][1], coords[1][1]]
        width = self.map.view.geometry().width()
        height = self.map.view.geometry().height()
        
        overlay_file = None
        legend = None
        plot_legend = False

        # There are now a few options:
        # 1) self.data has a make_overlay method
        # 2) self.data is a rioxarray DataArray
        #   a) with RGB values
        #   b) with scalar values 

        if self.data_has_map_overlay:

            # Let the object create the overlay

            fname = os.path.join(self.map.server_path, "overlays", self.file_name)
            okay = self.data.map_overlay(fname, xlim=lonlim, ylim=latlim, width=width)

            west = lonlim[0]
            east = lonlim[1]
            south = latlim[0]
            north = latlim[1] 

            if not okay:
                return

            overlay_file = f"./overlays/{self.file_name}"

            # If self.data has a legend attribute, pass it to the map
            # Legend can be a dict with color map info, or a file name !
            if hasattr(self.data, "legend"):
                legend = self.data.legend
                if "cmap" in legend and "cmin" in legend and "cmax" in legend:
                    cmin = legend["cmin"]
                    cmax = legend["cmax"]
                    cmap = cm.get_cmap(legend["cmap"])
                    plot_legend = True
           
        else:

            # Data should be a rioxarray DataArray or a method to get the data

            clip = True
            derefine = True
            data_is_rgb = False

            if self.get_data is not None:
                # There is a get_data method that needs to be called now. This is for example the case for the topography layer in Delft Dashboard.
                # This method should return a rioxarray DataArray
                self.data = self.get_data()
                clip = False # No need to clip, data is already for the current view
                derefine = False # No need to derefine, data is already for the current view

            # if self.data is still None, then it was never defined
            if self.data is None:
                return  

            if isinstance(self.data, (str, os.PathLike)):

                # File path with GeoTIFF. Read (again and again).

                if self.data_has_overview_levels:
                    # Determine max_cell_size based on map width and number of pixels
                    max_cell_size = (latlim[1] - latlim[0]) / height  # times 2 to be sure
                    # multiply to get meters (assume web mercator)
                    max_cell_size = max_cell_size * 111000
                    # Need to re-open the filen
                    with rasterio.open(self.data) as src:                    
                        overview_level, ok = get_appropriate_overview_level(src, max_cell_size)
                        data = rioxarray.open_rasterio(self.data, masked=False, overview_level=overview_level)
                        derefine = False # No derefining needed, overview level is used
                else:
                    # Get the entire dataset
                    data = rioxarray.open_rasterio(self.data, masked=False)        

                # If self.data has 3 or 4 bands, then it's RGB(A)
                if data.shape[0] == 3 or data.shape[0] == 4:
                    data_is_rgb = True
                else:
                    data_is_rgb = False
                    # Need to squeeze to 2D array
                    if data.shape[0] == 1:
                        data = data.squeeze("band", drop=True)

            else:

                data = self.data

            if clip:
                # Little buffer
                dlon = (lonlim[1] - lonlim[0]) / 10
                dlat = (latlim[1] - latlim[0]) / 10

                data = data.rio.clip_box(minx=lonlim[0]-dlon,
                                         miny=latlim[0]-dlat,
                                         maxx=lonlim[1]+dlon,
                                         maxy=latlim[1]+dlat,
                                         crs="EPSG:4326")
            if derefine:
                # Derefine data if too fine compared to screen resolution
                # Determine current resolution of data
                y = data["y"].values[:]
                if len(y) > 1:
                    dy = abs(y[1] - y[0])
                else:
                    dy = 1000000.0
                # if geographic, convert to meters m
                if data.rio.crs.is_geographic:
                    dy = dy * 111000     
                # Determine required resolution in metres based on lonlim, latlim, width, height
                req_dy = 0.5 * 111000 * (latlim[1] - latlim[0]) / height
                # Derefine if necessary
                if dy < req_dy:
                    # Derefine by a factor of 2, 4, 8, ...
                    fact = int(np.ceil(req_dy / dy))
                    # Find next power of 2
                    if fact <= 2:
                        fact = 2
                    elif fact <= 4:
                        fact = 4
                    elif fact <= 8:
                        fact = 8
                    elif fact <= 16:
                        fact = 16
                    elif fact <= 32:
                        fact = 32
                    else:
                        fact = 64    
                    data = data.isel(x=slice(0, None, fact), y=slice(0, None, fact))

            if data_is_rgb:

                # RGB data, y and rgb are already in the right order (top to bottom)

                plot_legend = False # No legend for RGB data

                x = data["x"].values[:]
                y = data["y"].values[:]
                rgb = data.values[:].astype(np.uint8)
                # rgb must be uint8
                # if rgb.dtype != np.uint8:
                #     rgb_float = rgb.astype(np.float32) 
                #     # Scale to 0–255
                #     rgb = np.clip(rgb_float / 65535 * 255, 0, 255).astype(np.uint8)                    
                # Add 4th band if not present
                if rgb.shape[0] == 3:
                    alpha = np.ones((1, rgb.shape[1], rgb.shape[2]), dtype=rgb.dtype) * 255
                    rgb = np.vstack((rgb, alpha))

            else:

                # Scalar data

                # Determine whether to use continuous or discrete color scale
                # Options are: 1) Discrete colors: layer has color_values
                #              2) Continuous colors: layer has no color_values
                #               a) use hillshading
                #               b) no hillshading  

                x = data["x"].values[:]
                y = data["y"].values[:]
                if y[0] < y[-1]:
                    y = np.flipud(y)
                    z = np.flipud(data.values[:])
                else:
                    z = data.values[:]

                # Generate RGB Numpy array 

                if self.color_values is not None:

                    # 1) Discrete colors

                    plot_legend = False # Legend is made in javascript

                    # Initialize an RGBA array with zeros
                    rgba = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.float32)
                    # Loop through color classes
                    contour = []

                    for icolor, color_value in enumerate(self.color_values):

                        # Add contour for legend
                        cnt = {}
                        cnt["color"] = color_value["color"]
                        # Get rgb float values for this color (between 0.0 and 1.0)
                        color_rgba = cm.colors.to_rgba(color_value["color"])
                        if "lower_value" in color_value and "upper_value" in color_value:
                            rgba[(z >= color_value["lower_value"]) & (z < color_value["upper_value"]), :] = color_rgba
                            if "text" in color_value:
                                cnt["text"] = color_value["text"]
                            else:
                                cnt["text"] = f"{color_value['lower_value']} - {color_value['upper_value']}"   
                        elif "lower_value" in color_value:
                            rgba[(z >= color_value["lower_value"]), :] = color_rgba
                            if "text" in color_value:
                                cnt["text"] = color_value["text"]
                            else:
                                cnt["text"] = f">= {color_value['lower_value']}"
                        elif "upper_value" in color_value:
                            rgba[(z < color_value["upper_value"]), :] = color_rgba
                            if "text" in color_value:
                                cnt["text"] = color_value["text"]
                            else:
                                cnt["text"] = f"< {color_value['upper_value']}"
                        contour.append(cnt)

                    rgb = rgba * 255
                    # Need to transpose so that shape is (4, height, width)
                    rgb = np.transpose(rgb, (2, 0, 1))

                    legend = {}
                    legend["title"] = self.legend_title
                    legend["contour"] = contour

                else:    

                    # 2) Continuous colors

                    plot_legend = True # Legend png needs to be made

                    # Color scale (cmin, cmax)
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

                    cmap = cm.get_cmap(self.color_map)    

                    if self.hillshading:
                        ls = LightSource(azdeg=315, altdeg=30)
                        dx = (x[1] - x[0]) / 2
                        dy = - (y[1] - y[0]) / 2
                        rgb = ls.shade(z, cmap,
                                    vmin=cmin,
                                    vmax=cmax,
                                    dx=dx*0.5,
                                    dy=dy*0.5,
                                    vert_exag=10.0,
                                    blend_mode="soft")
                        rgb = rgb * 255

                    else:
                        norm = matplotlib.colors.Normalize(vmin=cmin, vmax=cmax)
                        vnorm = norm(z)
                        rgb = cmap(vnorm) * 255

                    # Need to transpose so that shape is (4, height, width)
                    rgb = np.transpose(rgb, (2, 0, 1))    

            # Create xarray DataArray with RGBA values of the rgb array
            rgba_da = xr.DataArray(rgb,
                                dims=["band", "y", "x"],
                                coords={ "band": [0, 1, 2, 3], "y": y, "x": x})

            # 1. Assign CRS and spatial dims
            src_crs = data.rio.crs            
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

            overlay_file = "./overlays/" + self.file_name # To be used in call to javascript
            image.save(os.path.join(self.map.server_path, "overlays", self.file_name))


            # Overlay image has been created. Now check if it crosses the date line. If so, we need to split it in two images.

            # Get bounds in EPSG:3857
            left, bottom, right, top = rgba_3857.rio.bounds()

            # Reproject bounds to EPSG:4326
            transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
            west, south = transformer.transform(left, bottom)
            east, north = transformer.transform(right, top)

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


        if plot_legend:

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
            height = 1.5
            cm2png(cmap,
                file_name = os.path.join(self.map.server_path, "overlays", legend_file),
                orientation="vertical",
                legend_label=self.legend_label,
                vmin=cmin,
                vmax=cmax,
                width=width,
                height=height)

            # legend is a file name
            legend = "./overlays/" + legend_file

        if split_image:

            # Make the east layer visible
            self.map.runjs(self.main_js, "showLayer", arglist=[self.map_id + ".b", self.side])

            # Now we need to update the layers with the new bounds and opacity
            self.map.runjs("/js/raster_image_layer.js", "updateLayer",
                           id=self.map_id + ".a",
                           filename=overlay_file_a,
                           bounds=bounds_a,
                           colorbar=legend,
                           legend_position=self.legend_position,
                           side=self.side,
                           opacity=self.opacity)
            
            self.map.runjs("/js/raster_image_layer.js", "updateLayer",
                           id=self.map_id + ".b",
                           filename=overlay_file_b,
                           bounds=bounds_b,
                           side=self.side,
                           opacity=self.opacity)

        else:
            # Just update the layer with the new bounds and opacity
            self.map.runjs("/js/raster_image_layer.js", "updateLayer",
                           id=self.map_id + ".a",
                           filename=overlay_file,
                           bounds=bounds,
                           colorbar=legend,
                           legend_position=self.legend_position,
                           side=self.side,
                           opacity=self.opacity)

            # Make the east and west layers invisible
            self.map.runjs(self.main_js, "hideLayer", arglist=[self.map_id + ".b", self.side])

def get_appropriate_overview_level(
    src: rasterio.io.DatasetReader, max_pixel_size: float
) -> int:
    """
    Given a rasterio dataset `src` and a desired `max_pixel_size`,
    determine the appropriate overview level (zoom level) that fits
    the maximum resolution allowed by `max_pixel_size`.

    Parameters:
    src (rasterio.io.DatasetReader): The rasterio dataset reader object.
    max_pixel_size (float): The maximum pixel size for the resolution.

    Returns:
    int: The appropriate overview level.
    """
    # Get the original resolution (pixel size) in terms of x and y
    original_resolution = src.res  # Tuple of (x_resolution, y_resolution)
    if src.crs.is_geographic:
        original_resolution = (
            original_resolution[0] * 111000,
            original_resolution[1] * 111000,
        )  # Convert to meters
    # Get the overviews for the dataset
    overview_levels = src.overviews(
        1
    )  # Overview levels for the first band (if multi-band, you can adjust this)

    # If there are no overviews, return 0 (native resolution)
    if not overview_levels:
        return 0, False

    # Calculate the resolution for each overview by multiplying the original resolution by the overview factor
    resolutions = [
        (original_resolution[0] * factor, original_resolution[1] * factor)
        for factor in overview_levels
    ]

    # Find the highest overview level that is smaller than or equal to the max_pixel_size
    selected_overview = 0
    for i, (x_res, y_res) in enumerate(resolutions):
        if x_res <= max_pixel_size and y_res <= max_pixel_size:
            selected_overview = i
        else:
            break

    return selected_overview, True
