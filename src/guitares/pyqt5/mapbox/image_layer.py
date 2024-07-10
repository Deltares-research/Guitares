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
    def __init__(self, mapbox, id, map_id):
        super().__init__(mapbox, id, map_id)
        self.active = False
        self.type   = "image"
        self.file_name = map_id + ".png"

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


    def clear(self):
        self.active = False
        js_string = "import('/js/main.js').then(module => {module.removeLayer('" + self.id + "')});"
        self.mapbox.view.page().runJavaScript(js_string)

    def make_overlay(self):    
        fname = os.path.join(self.mapbox.server_path, "overlays", self.file_name)
        coords = self.mapbox.map_extent
        xlim = [coords[0][0], coords[1][0]]
        ylim = [coords[0][1], coords[1][1]]
        width = self.mapbox.view.geometry().width()
        okay = self.data.map_overlay(fname, xlim=xlim, ylim=ylim, width=width)
        if okay:
            return xlim, ylim
        else:
            return None, None

    def update(self):
        if hasattr(self.data, "map_overlay"):
            xlim, ylim = self.make_overlay()
            if xlim is None:
                return
            bounds = [[xlim[0], xlim[1]], [ylim[0], ylim[1]]]
            bounds_string = f"[[{bounds[0][0]},{bounds[0][1]}],[{bounds[1][0]},{bounds[1][1]}]]"
            overlay_file = f"./overlays/{self.file_name}"
            js_string = f"import('/js/image_layer.js').then(module => {{module.updateLayer('{overlay_file}', '{self.map_id}', {bounds_string}, '')}});"
            self.mapbox.view.page().runJavaScript(js_string)
            js_string = f"import('/js/image_layer.js').then(module => {{module.setOpacity('{self.map_id}', 1.0)}});"
            self.mapbox.view.page().runJavaScript(js_string)
            

    def set_data(self, data, image_file=None, xlim=None, ylim=None):
        fname = os.path.join(self.mapbox.server_path, "overlays", self.file_name)
        self.data = data

        js_string = f"import('/js/main.js').then(module => {{module.removeLayer('{self.map_id}')}});"
        self.mapbox.view.page().runJavaScript(js_string)

        try:
            xlim, ylim = self.make_overlay()
            if xlim is None:
                return
        except Exception as e:
            print(f"Something went wrong with map overlay: {self.map_id}, {e}")
            return

        bounds = [[xlim[0], xlim[1]], [ylim[0], ylim[1]]]
        bounds_string = f"[[{bounds[0][0]},{bounds[0][1]}],[{bounds[1][0]},{bounds[1][1]}]]"
        overlay_file = f"./overlays/{self.file_name}"
        js_string = f"import('/js/image_layer.js').then(module => {{module.addLayer('{overlay_file}', '{self.map_id}', {bounds_string}, '')}});"
        self.mapbox.view.page().runJavaScript(js_string)

    # def set_data(self,
    #              data,
    #              image_file=None,
    #              xlim=None,
    #              ylim=None):
        
    #     fname = os.path.join(self.mapbox.server_path, "overlays", self.file_name)

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

        # shutil.copy(image_file, os.path.join(self.mapbox.server_path, "overlays", self.file_name))

        # js_string = "import('/js/main.js').then(module => {module.removeLayer('" + self.map_id + "')});"
        # self.mapbox.view.page().runJavaScript(js_string)

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
        # self.mapbox.view.page().runJavaScript(js_string)


#         overlay_file = "./overlays/" + "main.background_topography.png"

#         # Bounds
#         bounds = [[xlim[0], xlim[1]], [ylim[0], ylim[1]]]
#         bounds_string = "[[" + str(bounds[0][0]) + "," + str(bounds[0][1]) + "],[" + str(bounds[1][0]) + "," + str(bounds[1][1]) + "]]"

# #        overlay_file = ""

#         js_string = "import('/js/image_layer.js').then(module => {module.addLayer('" + overlay_file + "','" + self.map_id + "'," + bounds_string + ","")});"
#         self.mapbox.view.page().runJavaScript(js_string)

# #        self.update()

