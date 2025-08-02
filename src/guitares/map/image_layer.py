import glob
import os
import numpy as np
from guitares.colormap import cm2png
from .layer import Layer
from .colorbar import ColorBar

class ImageLayer(Layer):
    def __init__(self, map, id, map_id, **kwargs):
        super().__init__(map, id, map_id, **kwargs)
        self.active = False
        self.type   = "image"
        self.file_name = map_id + ".png"
        self.colorbar = None
        self.xlim = None
        self.ylim = None
        
    def activate(self):
        self.active = True
        self.show()

    def deactivate(self):
        self.active = False

    def clear(self):
        self.active = False
        # js_string = "import('/js/main.js').then(module => {module.removeLayer('" + self.map_id + "')});"
        # self.map.view.page().runJavaScript(js_string)
        self.map.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])

    def show(self):
        self.visible = True # to make sure update is run
        coords = self.map.map_extent
        xlim = [coords[0][0], coords[1][0]]
        ylim = [coords[0][1], coords[1][1]]
        if not (xlim == self.xlim and ylim == self.ylim):
            self.update() # Update the layer if the extent has changed
        super().show()  # Call the parent class method
    
    def make_overlay(self):    
        fname = os.path.join(self.map.server_path, "overlays", self.file_name)
        coords = self.map.map_extent
        xlim = [coords[0][0], coords[1][0]]
        ylim = [coords[0][1], coords[1][1]]
        width = self.map.view.geometry().width()
        okay = self.data.map_overlay(fname, xlim=xlim, ylim=ylim, width=width)
        if okay:
            self.xlim = xlim
            self.ylim = ylim
            return xlim, ylim
        else:
            return None, None

    def update(self):
        if hasattr(self.data, "map_overlay") and self.visible:
            xlim, ylim = self.make_overlay()
            if xlim is None:
                return
            # if xlim[0] > xlim[1]:
            #     xlim[0] -= 360.0
            bounds = [[xlim[0], xlim[1]], [ylim[0], ylim[1]]]
            overlay_file = f"./overlays/{self.file_name}"
            self.map.runjs("/js/image_layer.js", "updateLayer", arglist=[overlay_file, self.map_id, bounds, self.colorbar, self.side])
            self.map.runjs("/js/image_layer.js", "setOpacity", arglist=[self.map_id, self.opacity, self.side])

    def set_data(self, data, image_file=None, xlim=None, ylim=None, colorbar=False):

        self.data = data
        self.map.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])

        try:
            xlim, ylim = self.make_overlay()
            if xlim is None:
                return
        except Exception as e:
            print(f"Something went wrong with map overlay: {self.map_id}, {e}")
            return

        if colorbar and self.side != "b":
            self.colorbar = self.make_colorbar()
        else:
            self.colorbar = ""
        
        bounds = [[xlim[0], xlim[1]], [ylim[0], ylim[1]]]
        overlay_file = f"./overlays/{self.file_name}"
        self.map.runjs("/js/image_layer.js", "addLayer", arglist=[overlay_file, self.map_id, bounds, self.colorbar, self.side])
        self.map.runjs("/js/image_layer.js", "setOpacity", arglist=[self.map_id, self.opacity, self.side])
        if self.side != "b":
            self.map.runjs("/js/image_layer.js", "setLegendPosition", arglist=[self.map_id, self.legend_position, self.side])
    
    def make_colorbar(self,):
        if self.color_values:
            clrbar = ColorBar(color_values=self.color_values, legend_title=self.legend_title)
            clrbar.make(0.0, 0.0, decimals=self.decimals)
            clrbar_dict = clrbar.to_dict()
        else:
            # Make colorbar image and send url to js
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
            cm2png(self.data.cmap,
                file_name = os.path.join(self.map.server_path, "overlays", legend_file),
                orientation="vertical",
                vmin=self.data.cmin,
                vmax=self.data.cmax,
                legend_title=self.legend_title,
                legend_label=self.legend_label,
                label_size=7,
                tick_size=5,
                units=self.legend_units,
                decimals=self.legend_decimals,
                width=0.5,
                height=1)

            clrbar_dict = "./overlays/" + legend_file
        return clrbar_dict

