import os

from .colorbar import ColorBar
from .layer import Layer
from cht_tiling.tiling import make_floodmap_overlay

class RasterFromTilesLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        self.new    = True
        self.file_name = map_id + ".png"

    def set_data(self, data):
        self.data = data
        self.update()

    def update(self):
        if self.data is None or not self.get_visibility():
            return
        overlay_file = os.path.join(self.mapbox.server_path, 'overlays', self.file_name)
        overlay_url  = "./overlays/" + self.file_name
        coords = self.mapbox.map_extent
        xl = [coords[0][0], coords[1][0]]
        yl = [coords[0][1], coords[1][1]]
        wdt = self.mapbox.view.geometry().width()
        hgt = self.mapbox.view.geometry().height()
        xb, yb = make_floodmap_overlay(self.data,
                                       self.index_path,
                                       self.topobathy_path,
                                       npixels=[wdt, hgt],
                                       lon_range=xl,
                                       lat_range=yl,  
                                       option="deterministic",
                                       color_values=self.color_values,
                                       caxis=None,
                                       zbmax=self.zbmax,
                                       depth=None,
                                       quiet=False,
                                       file_name=overlay_file)
        # Bounds
        bounds = [[xb[0], xb[1]], [yb[0], yb[1]]]

        # Legend
        clrbar = ColorBar(color_values=self.color_values, legend_title=self.legend_title)
        clrbar.make(0.0, 0.0, decimals=self.decimals)
        clrbar_dict = clrbar.to_dict()

        if self.new:
            self.mapbox.runjs("/js/image_layer.js", "addLayer", arglist=[overlay_url, self.map_id, bounds, clrbar_dict, self.side])
        else:
            self.mapbox.runjs("/js/image_layer.js", "updateLayer", arglist=[overlay_url, self.map_id, bounds, clrbar_dict, self.side])
        self.mapbox.runjs("/js/image_layer.js", "setOpacity", arglist=[self.map_id, self.opacity, self.side])
        self.new = False

    def redraw(self):
        self.new = True
        self.update()
        if not self.get_visibility():
            self.set_visibility(False)
