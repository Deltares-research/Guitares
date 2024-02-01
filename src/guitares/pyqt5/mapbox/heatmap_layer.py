from .layer import Layer
from geopandas import GeoDataFrame

class HeatmapLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(self, data, density_property=""):
        self.data = data
        self.density_property = density_property
        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                self.data = GeoDataFrame()
        self.visible = True 
        # Add new layer
        self.mapbox.runjs(
            "./js/heatmap_layer.js",
            "addLayer",
            arglist=[
                self.map_id,
                self.data,
                self.max_zoom,
                self.density_property,
                self.side
            ],
        )

    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)
        if not self.get_visibility():
            self.set_visibility(False)

    # def activate(self):
    #     self.active = True

    # def deactivate(self):
    #     self.active = False

    # def clear(self):
    #     self.active = False
    #     self.remove()

    # def remove(self):
    #     self.mapbox.runjs(self.main_js, "removeLayer", arglist=[self.map_id, self.side])

    # def update(self):
    #     # This layer does not get updated when zooming in or out
    #     pass

    # def set_visibility(self, true_or_false):
    #     if true_or_false:
    #         self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id])
    #     else:
    #         self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id])
