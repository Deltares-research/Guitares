import os
import time

import rasterio
import rasterio.features
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio import MemoryFile
from rasterio.transform import Affine
import shutil

from .layer import Layer

class ImageLayer(Layer):
    def __init__(self, map, id, map_id, **kwargs):
        super().__init__(map, id, map_id, **kwargs)

        self.active = False
        self.type   = "image"
        self.file_name = map_id + ".png"

    def activate(self):

        self.active = True
        self.show()

    def deactivate(self):

        self.active = False

    def clear(self):

        self.active = False
        self.map.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])

    def set_data(self, data, image_file=None, xlim=None, ylim=None):

        # If data is a string or a path, assume it is an image file
        if isinstance(data, (str, os.PathLike)):
            # Read the image file (lazily)
            data = rasterio.open(image_file)

        self.data = data

        # self.map.runjs("/js/image_layer.js", "addLayer", arglist=[self.map_id])
        self.map.runjs("/js/image_layer.js",
                       "addLayer",
                       id=self.map_id,
                       side=self.side)

        self.update()

    def update(self):

        coords = self.map.map_extent
        xlim = [coords[0][0], coords[1][0]]
        ylim = [coords[0][1], coords[1][1]]
        width = self.map.view.geometry().width()

        overlay_file = None
        legend = None

        if hasattr(self.data, "map_overlay"):

            fname = os.path.join(self.map.server_path, "overlays", self.file_name)
            okay = self.data.map_overlay(fname, xlim=xlim, ylim=ylim, width=width)
            # xlim, ylim = self.make_overlay()

            if not okay:
                return

            bounds = [[xlim[0], xlim[1]], [ylim[0], ylim[1]]]
            overlay_file = f"./overlays/{self.file_name}"

            # If self.data has a legend attribute, pass it to the map
            if hasattr(self.data, "legend"):
                legend = self.data.legend

        # check if self.data is a rasterio dataset
        elif isinstance(self.data, rasterio.io.DatasetReader):
            pass

            # # Get bounds
            # bnds = self.data.bounds
            # bounds = [[bnds.left, bnds.right], [bnds.bottom, bnds.top]]
            # # Copy the file to the overlays folder
            # # Need to make a png file from the dataset within the bound
            # fname = os.path.join(self.map.server_path, "overlays", "image.png")
            # # Reproject to web mercator
            # src_crs = self.data.crs
            # dst_crs = 'EPSG:3857'
            # transform, width, height = calculate_default_transform(
            #     self.data.crs, dst_crs, self.data.width, self.data.height, *self.data.bounds)
            # kwargs = self.data.meta.copy()
            # kwargs.update({
            #     'crs': dst_crs,
            #     'transform': transform,
            #     'width': width,
            #     'height': height
            # })


        if overlay_file:
            self.map.runjs("/js/image_layer.js", "updateLayer",
                           id=self.map_id,
                           filename=overlay_file,
                           bounds=bounds,
                           colorbar=legend,
                           legend_position=self.legend_position,
                           side=self.side,
                           opacity=self.opacity)
        # self.map.runjs("/js/image_layer.js", "setOpacity", id=self.map_id, opacity=self.opacity)
            # self.map.runjs("/js/image_layer.js", "setOpacity", arglist=[self.map_id, self.opacity])
            # if legend is not None:
            #     self.map.runjs("/js/image_layer.js", "setLegendPosition", arglist=[self.map_id, self.legend_position, self.side])

    def set_opacity(self, opacity):
        self.opacity = opacity
        # self.map.runjs("/js/image_layer.js", "setOpacity", arglist=[self.map_id, opacity])
        self.map.runjs("/js/image_layer.js",
                       "setOpacity",
                       id=self.map_id,
                       opacity=self.opacity)

    # def set_data(self,
    #              data,
    #              image_file=None,
    #              xlim=None,
    #              ylim=None):
        
    #     fname = os.path.join(self.map.server_path, "overlays", self.file_name)

    #     self.data = data

        # id_string = self.id

        # dataset = rasterio.open(image_file)

        # src_crs = 'EPSG:4326'
        # dst_crs = 'EPSG:3857'

        # with rasterio.open(image_file) as src:
        #     transform, width, height = calculate_default_transform(
        #         src.crs, dst_crs, src.width, src.height, *src.bounds)
        #     kwargs = src.meta.copy()
        #     kwargs.update({
        #         'crs': dst_crs,
        #         'transform': transform,
        #         'width': width,
        #         'height': height
        #     })
        #     bnds = src.bounds

        #     mem_file = MemoryFile()
        #     with mem_file.open(**kwargs) as dst:
        #         for i in range(1, src.count + 1):
        #             reproject(
        #                 source=rasterio.band(src, i),
        #                 destination=rasterio.band(dst, i),
        #                 src_transform=src.transform,
        #                 src_crs=src.crs,
        #                 dst_transform=transform,
        #                 dst_crs=dst_crs,
        #                 resampling=Resampling.nearest)

        #         # band1 = dst.read(1)

        # new_bounds = transform_bounds(dst_crs, src_crs,
        #                               dst.bounds[0],
        #                               dst.bounds[1],
        #                               dst.bounds[2],
        #                               dst.bounds[3])
        # isn = np.where(band1 < 0.001)
        # band1[isn] = np.nan

        # band1 = np.flipud(band1)
        # cminimum = np.nanmin(band1)
        # cmaximum = np.nanmax(band1)

        # norm = matplotlib.colors.Normalize(vmin=cminimum, vmax=cmaximum)
        # vnorm = norm(band1)

        # cmap = cm.get_cmap(colormap)
        # im = Image.fromarray(np.uint8(cmap(vnorm) * 255))

        # shutil.copy(image_file, os.path.join(self.map.server_path, "overlays", self.file_name))

        # js_string = "import('/js/main.js').then(module => {module.removeLayer('" + self.map_id + "')});"
        # self.map.view.page().runJavaScript(js_string)

        # try:
        #     xlim, ylim = self.make_overlay()
        #     if xlim is None:
        #         return
        # except:
        #     print("Something went wrong with map overlay : " + self.map_id)
        #     return
        # bounds = [[xlim[0], xlim[1]], [ylim[0], ylim[1]]]
        # bounds_string = "[[" + str(bounds[0][0]) + "," + str(bounds[0][1]) + "],[" + str(bounds[1][0]) + "," + str(bounds[1][1]) + "]]"
        # overlay_file = "./overlays/" + self.file_name
        # js_string = "import('/js/image_layer.js').then(module => {module.addLayer('" + overlay_file + "','" + self.map_id + "'," + bounds_string + ","")});"
        # self.map.view.page().runJavaScript(js_string)


#         overlay_file = "./overlays/" + "main.background_topography.png"

#         # Bounds
#         bounds = [[xlim[0], xlim[1]], [ylim[0], ylim[1]]]
#         bounds_string = "[[" + str(bounds[0][0]) + "," + str(bounds[0][1]) + "],[" + str(bounds[1][0]) + "," + str(bounds[1][1]) + "]]"

# #        overlay_file = ""

#         js_string = "import('/js/image_layer.js').then(module => {module.addLayer('" + overlay_file + "','" + self.map_id + "'," + bounds_string + ","")});"
#         self.map.view.page().runJavaScript(js_string)

# #        self.update()

