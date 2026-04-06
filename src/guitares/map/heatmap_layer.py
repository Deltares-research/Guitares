"""Heatmap layer for visualising point density on the map."""

from typing import Any, Union

from geopandas import GeoDataFrame

from .layer import Layer


class HeatmapLayer(Layer):
    """Heatmap layer rendering point density as a colour gradient.

    Parameters
    ----------
    map : Any
        The parent map object.
    id : str
        Logical layer identifier.
    map_id : str
        Fully qualified JS-side layer identifier.
    **kwargs : Any
        Passed through to ``Layer.__init__``.
    """

    def __init__(self, map: Any, id: str, map_id: str, **kwargs: Any) -> None:
        super().__init__(map, id, map_id, **kwargs)

    def set_data(
        self, data: Union[GeoDataFrame, Any], density_property: str = ""
    ) -> None:
        """Set point data and render the heatmap layer.

        Parameters
        ----------
        data : GeoDataFrame
            Point geometries to visualise as a heatmap.
        density_property : str, optional
            Name of the property used to weight heatmap intensity.
        """
        self.data = data
        self.density_property = density_property
        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            if len(data) == 0:
                self.data = GeoDataFrame()
        self.visible = True
        # Add new layer
        self.map.runjs(
            "/js/heatmap_layer.js",
            "addLayer",
            arglist=[
                self.map_id,
                self.data,
                self.max_zoom,
                self.density_property,
                self.side,
            ],
        )

    def redraw(self) -> None:
        """Redraw the layer (e.g. after a style change)."""
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)
        if not self.get_visibility():
            self.set_visibility(False)
