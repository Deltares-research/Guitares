import os
import glob
import numpy as np
from .colorbar import ColorBar
from .layer import Layer
from guitares.colormap import cm2png

from cht_tiling.tiling import make_floodmap_overlay_v2, make_topo_overlay_v2

class RasterFromTilesLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        self.new    = True
        self.file_name = map_id + ".png"

    def set_data(self, data):
        self.data = data
        self.update()

    def update(self):
        if not self.get_visibility():
            return
        if self.data is None and self.option == "flood_map":
            return
        overlay_file = os.path.join(self.mapbox.server_path, 'overlays', self.file_name)
        overlay_url  = "./overlays/" + self.file_name
        coords = self.mapbox.map_extent
        xl = [coords[0][0], coords[1][0]]
        yl = [coords[0][1], coords[1][1]]
        wdt = self.mapbox.view.geometry().width()
        hgt = self.mapbox.view.geometry().height()

        # Adjust quality
        if self.quality == "high":
            # No need to do anything (using full screen resolution)
            pass
        elif self.quality == "medium":
            wdt = int(wdt / 2)
            hgt = int(hgt / 2)
        elif self.quality == "low":
            wdt = int(wdt / 4)
            hgt = int(hgt / 4)

        if self.option == "topography":

            xb, yb, cb = make_topo_overlay_v2(self.topobathy_path,
                                              lon_range=xl,
                                              lat_range=yl,
                                              hillshading=self.hillshading,
                                              hillshading_exaggeration=self.hillshading_exaggeration,
                                              hillshading_azimuth=self.hillshading_azimuth,
                                              hillshading_altitude=self.hillshading_altitude,
                                              npixels=[wdt, hgt],
                                              color_map=self.color_map,
                                              color_range=[self.color_scale_cmin, self.color_scale_cmax],
                                              color_scale_auto=self.color_scale_auto,
                                              color_scale_symmetric=self.color_scale_symmetric,
                                              color_scale_symmetric_side=self.color_scale_symmetric_side,                                       
                                              quiet=False,
                                              file_name=overlay_file)

            cmin = cb[0]
            cmax = cb[1]

        elif self.option == "flood_map":
            xb, yb = make_floodmap_overlay_v2(self.data,
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

        if xb is None:
            # Something went wrong when making the overlay
            return

        # Bounds
        bounds = [[xb[0], xb[1]], [yb[0], yb[1]]]

        # Legend
        if self.color_values:
            clrbar = ColorBar(color_values=self.color_values, legend_title=self.legend_title)
            clrbar.make(0.0, 0.0, decimals=self.decimals)
            clrbar_dict = clrbar.to_dict()

        else:
            # Make colorbar image and send url to js
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
            # Multiply cmin and cmax by scale factor
            cmin = cmin * self.scale_factor
            cmax = cmax * self.scale_factor
            cm2png(self.color_map,
                file_name = os.path.join(self.mapbox.server_path, "overlays", legend_file),
                orientation="vertical",
                vmin=cmin,
                vmax=cmax,
                legend_title=self.legend_title,
                legend_label=self.legend_label,
                units=self.legend_units,
                decimals=self.legend_decimals)

            clrbar_dict = "./overlays/" + legend_file

        if self.new:
            self.mapbox.runjs("/js/image_layer.js", "addLayer", arglist=[overlay_url, self.map_id, bounds, clrbar_dict, self.side])
            # Set legend position (should make this generic for all layers)
            self.mapbox.runjs("/js/image_layer.js", "setLegendPosition", arglist=[self.map_id, self.legend_position, self.side])
        else:
            self.mapbox.runjs("/js/image_layer.js", "updateLayer", arglist=[overlay_url, self.map_id, bounds, clrbar_dict, self.side])
        self.mapbox.runjs("/js/image_layer.js", "setOpacity", arglist=[self.map_id, self.opacity, self.side])
        self.new = False

    def redraw(self):
        self.new = True
        self.update()
        if not self.get_visibility():
            self.set_visibility(False)
